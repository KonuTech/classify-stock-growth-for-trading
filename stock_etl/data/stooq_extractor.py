"""Stooq data extraction and processing."""

import pandas as pd
import requests
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.models import StooqRecord, InstrumentType

logger = structlog.get_logger(__name__)


class StooqExtractor:
    """Extract stock and index data from Stooq service."""
    
    def __init__(self, base_url: str = "https://stooq.com/q/d/l/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def _build_stooq_url(self, symbol: str, period: str = "d", interval: str = "1") -> str:
        """Build Stooq download URL for a symbol."""
        # Stooq URL format: https://stooq.com/q/d/l/?s=SYMBOL&f=CSV&i=d
        params = {
            's': symbol.upper(),
            'f': 'csv',
            'i': period,  # d=daily, w=weekly, m=monthly
        }
        
        url = self.base_url + "?"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        
        logger.debug("Built Stooq URL", symbol=symbol, url=url)
        return url
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda retry_state: logger.warning(
            "Retrying Stooq download",
            symbol=retry_state.kwargs.get('symbol'),
            attempt=retry_state.attempt_number
        )
    )
    def download_symbol_data(
        self, 
        symbol: str, 
        period: str = "d", 
        save_to_file: Optional[Path] = None
    ) -> Optional[str]:
        """Download raw CSV data for a symbol from Stooq."""
        try:
            url = self._build_stooq_url(symbol, period)
            
            logger.info("Downloading data from Stooq", symbol=symbol, url=url)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if we got actual data (not an error page)
            if len(response.content) < 100:
                logger.warning("Received minimal data from Stooq", symbol=symbol, size=len(response.content))
                return None
            
            # Check for common error indicators
            content = response.text
            content_lines = content.split('\n')
            logger.debug("Received content from Stooq", symbol=symbol, size=len(content), lines=len(content_lines), first_line=content_lines[0] if content_lines else "")
            
            if "Not Found" in content or "Error" in content or len(content_lines) < 3:
                logger.warning("Received error or insufficient data from Stooq", symbol=symbol, lines=len(content_lines), first_few_lines=content_lines[:3])
                return None
            
            # Save to file if requested
            if save_to_file:
                save_to_file.parent.mkdir(parents=True, exist_ok=True)
                with open(save_to_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info("Data saved to file", symbol=symbol, file_path=str(save_to_file))
            
            logger.info("Successfully downloaded data", symbol=symbol, size=len(content))
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to download data from Stooq", symbol=symbol, error=str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error downloading data", symbol=symbol, error=str(e))
            raise
    
    def parse_csv_data(self, csv_content: str, symbol: str) -> List[StooqRecord]:
        """Parse Stooq CSV data into validated records."""
        try:
            # Read CSV using pandas
            from io import StringIO
            df = pd.read_csv(StringIO(csv_content))
            
            # Check for modern format (Date,Open,High,Low,Close,Volume)
            expected_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in expected_columns):
                missing_cols = [col for col in expected_columns if col not in df.columns]
                logger.error("Missing expected columns in CSV", symbol=symbol, missing_columns=missing_cols, available_columns=list(df.columns))
                return []
            
            # Convert to records and validate
            records = []
            for idx, row in df.iterrows():
                try:
                    # Create record dict from row
                    record_data = row.to_dict()
                    
                    # Create StooqRecord with validation
                    record = StooqRecord(**record_data)
                    # Set ticker and period programmatically
                    record.ticker = symbol.upper()
                    record.period = "D"
                    
                    records.append(record)
                    
                except Exception as e:
                    logger.warning(
                        "Failed to validate record",
                        symbol=symbol,
                        row_index=idx,
                        error=str(e),
                        row_data=row.to_dict()
                    )
                    continue
            
            logger.info(
                "Parsed CSV data",
                symbol=symbol,
                total_rows=len(df),
                valid_records=len(records),
                invalid_records=len(df) - len(records)
            )
            return records
            
        except Exception as e:
            logger.error("Failed to parse CSV data", symbol=symbol, error=str(e))
            return []
    
    def extract_symbol(
        self, 
        symbol: str, 
        instrument_type: InstrumentType,
        save_directory: Optional[Path] = None
    ) -> List[StooqRecord]:
        """Extract and parse data for a single symbol."""
        try:
            # Determine save file path
            save_file = None
            if save_directory:
                type_dir = save_directory / "daily" / "pl" / f"wse-{instrument_type.value}s"
                save_file = type_dir / f"{symbol.lower()}.txt"
            
            # Download data
            csv_content = self.download_symbol_data(symbol, save_to_file=save_file)
            if not csv_content:
                return []
            
            # Parse and validate
            records = self.parse_csv_data(csv_content, symbol)
            
            logger.info(
                "Successfully extracted symbol data",
                symbol=symbol,
                instrument_type=instrument_type.value,
                records_count=len(records),
                date_range=f"{records[-1].trading_date} to {records[0].trading_date}" if records else "No data"
            )
            
            return records
            
        except Exception as e:
            logger.error(
                "Failed to extract symbol data",
                symbol=symbol,
                instrument_type=instrument_type.value,
                error=str(e)
            )
            return []
    
    def extract_multiple_symbols(
        self,
        symbols: Dict[str, InstrumentType],
        save_directory: Optional[Path] = None,
        delay_between_requests: float = 1.0
    ) -> Dict[str, List[StooqRecord]]:
        """Extract data for multiple symbols with rate limiting."""
        import time
        
        results = {}
        total_symbols = len(symbols)
        
        logger.info("Starting bulk symbol extraction", total_symbols=total_symbols)
        
        for i, (symbol, instrument_type) in enumerate(symbols.items(), 1):
            logger.info(
                "Processing symbol",
                symbol=symbol,
                progress=f"{i}/{total_symbols}",
                instrument_type=instrument_type.value
            )
            
            try:
                records = self.extract_symbol(symbol, instrument_type, save_directory)
                results[symbol] = records
                
                # Rate limiting
                if i < total_symbols and delay_between_requests > 0:
                    time.sleep(delay_between_requests)
                    
            except Exception as e:
                logger.error(
                    "Failed to process symbol in bulk extraction",
                    symbol=symbol,
                    error=str(e)
                )
                results[symbol] = []
        
        successful_extractions = sum(1 for records in results.values() if records)
        total_records = sum(len(records) for records in results.values())
        
        logger.info(
            "Completed bulk symbol extraction",
            total_symbols=total_symbols,
            successful_extractions=successful_extractions,
            total_records=total_records
        )
        
        return results
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
        logger.info("Stooq extractor session closed")


def get_polish_market_symbols() -> Dict[str, InstrumentType]:
    """Get a predefined list of Polish market symbols for testing."""
    return {
        # Stocks
        'XTB': InstrumentType.STOCK,
        'PKN': InstrumentType.STOCK,
        'CCC': InstrumentType.STOCK,
        'LPP': InstrumentType.STOCK,
        'CDR': InstrumentType.STOCK,
        
        # Indices
        'WIG': InstrumentType.INDEX,
        'WIG20': InstrumentType.INDEX,
        'MWIG40': InstrumentType.INDEX,
        'SWIG80': InstrumentType.INDEX,
    }


def extract_sample_data(
    output_directory: Optional[Path] = None,
    symbols: Optional[Dict[str, InstrumentType]] = None
) -> Dict[str, List[StooqRecord]]:
    """Extract sample data for testing purposes."""
    if symbols is None:
        symbols = get_polish_market_symbols()
    
    if output_directory is None:
        output_directory = Path("data")
    
    extractor = StooqExtractor()
    try:
        return extractor.extract_multiple_symbols(
            symbols=symbols,
            save_directory=output_directory,
            delay_between_requests=2.0  # Be respectful to Stooq servers
        )
    finally:
        extractor.close()