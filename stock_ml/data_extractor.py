"""
Data extraction module for stock data from PostgreSQL database.
Supports extracting data for multiple instruments and training separate models.
"""

import pandas as pd
import numpy as np
import psycopg2
from typing import Tuple, Optional, List, Dict
import logging
from datetime import datetime
from pathlib import Path

# Set up logging using centralized configuration
try:
    from .logging_config import get_ml_logger
except ImportError:
    from logging_config import get_ml_logger
logger = get_ml_logger(__name__)


class MultiStockDataExtractor:
    """Extract stock data from PostgreSQL database for multiple instruments"""
    
    def __init__(self, db_config: dict = None):
        """
        Initialize the data extractor
        
        Args:
            db_config: Database configuration dictionary
        """
        self.db_config = db_config or {
            'host': 'localhost',
            'port': '5432',
            'database': 'stock_data',
            'user': 'postgres',
            'password': 'postgres'
        }
        self.pg_conn = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.pg_conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
            
    def get_available_stocks(self) -> List[str]:
        """
        Get list of all available stock symbols in the database
        
        Returns:
            List of stock symbols
        """
        if not self.pg_conn:
            self.connect()
            
        query = """
        SELECT DISTINCT bi.symbol
        FROM test_stock_data.base_instruments AS bi
        JOIN test_stock_data.stock_prices AS sp ON bi.id = sp.stock_id
        WHERE bi.instrument_type = 'stock'
        ORDER BY bi.symbol;
        """
        
        try:
            result = pd.read_sql_query(query, self.pg_conn)
            symbols = result['symbol'].tolist()
            
            logger.info(f"Found {len(symbols)} available stocks: {symbols}")
            return symbols
            
        except Exception as e:
            logger.error(f"Failed to get available stocks: {e}")
            raise
            
    def extract_all_stocks_data(self) -> Dict[str, pd.DataFrame]:
        """
        Extract data for all available stocks
        
        Returns:
            Dictionary mapping symbol -> DataFrame
        """
        stocks = self.get_available_stocks()
        all_data = {}
        
        for symbol in stocks:
            try:
                df = self.extract_single_stock_data(symbol)
                if not df.empty:
                    all_data[symbol] = df
                    logger.info(f"Successfully extracted {len(df)} records for {symbol}")
                else:
                    logger.warning(f"No data found for {symbol}")
            except Exception as e:
                logger.error(f"Failed to extract data for {symbol}: {e}")
                continue
                
        logger.info(f"Successfully extracted data for {len(all_data)} stocks")
        return all_data
            
    def extract_single_stock_data(self, symbol: str) -> pd.DataFrame:
        """
        Extract data for a single stock symbol
        
        Args:
            symbol: Stock symbol to extract
            
        Returns:
            DataFrame with columns: symbol, currency, close_price, volume, trading_date_local
        """
        if not self.pg_conn:
            self.connect()
            
        query = """
        SELECT
            bi.symbol,
            bi.currency,
            sp.close_price,
            sp.volume,
            sp.trading_date_local
        FROM
            test_stock_data.base_instruments AS bi
        JOIN
            test_stock_data.stock_prices AS sp ON bi.id = sp.stock_id
        WHERE
            bi.symbol = %s
        ORDER BY
            sp.trading_date_local ASC;
        """
        
        try:
            df = pd.read_sql_query(query, self.pg_conn, params=[symbol])
            
            # Validate data
            if df.empty:
                logger.warning(f"No data found for symbol: {symbol}")
                return pd.DataFrame()
                
            # Convert date column to datetime
            df['trading_date_local'] = pd.to_datetime(df['trading_date_local'])
            
            # Data quality checks
            self._validate_data_quality(df, symbol)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to extract data for {symbol}: {e}")
            raise
            
    def _validate_data_quality(self, df: pd.DataFrame, symbol: str):
        """Validate data quality for a specific stock"""
        checks = {
            'missing_values': df.isnull().sum().sum(),
            'duplicate_dates': df['trading_date_local'].duplicated().sum(),
            'non_positive_prices': (df['close_price'] <= 0).sum(),
            'negative_volume': (df['volume'] < 0).sum(),
        }
        
        # Always log data quality checks at INFO level
        logger.info(f"Data quality check for {symbol}: {checks}")
        
        # Log specific issues as warnings
        if checks['non_positive_prices'] > 0:
            logger.warning(f"{symbol}: Found {checks['non_positive_prices']} non-positive prices")
        if checks['negative_volume'] > 0:
            logger.warning(f"{symbol}: Found {checks['negative_volume']} negative volumes")
        if checks['duplicate_dates'] > 0:
            logger.warning(f"{symbol}: Found {checks['duplicate_dates']} duplicate dates")
        
        # Log summary of data quality status
        total_issues = sum(checks.values())
        if total_issues == 0:
            logger.info(f"{symbol}: ✅ Data quality validation passed")
        else:
            logger.warning(f"{symbol}: ⚠️ Found {total_issues} total data quality issues")
            
    def filter_stocks_by_data_quality(self, all_data: Dict[str, pd.DataFrame], 
                                    min_records: int = 500,
                                    min_years: float = 2.0) -> Dict[str, pd.DataFrame]:
        """
        Filter stocks based on data quality criteria
        
        Args:
            all_data: Dictionary of stock data
            min_records: Minimum number of records required
            min_years: Minimum years of data required
            
        Returns:
            Filtered dictionary of stock data
        """
        filtered_data = {}
        
        for symbol, df in all_data.items():
            if len(df) < min_records:
                logger.info(f"Excluding {symbol}: Only {len(df)} records (need >= {min_records})")
                continue
                
            date_range = (df['trading_date_local'].max() - df['trading_date_local'].min()).days / 365.25
            if date_range < min_years:
                logger.info(f"Excluding {symbol}: Only {date_range:.1f} years of data (need >= {min_years})")
                continue
                
            filtered_data[symbol] = df
            logger.info(f"Keeping {symbol}: {len(df)} records, {date_range:.1f} years")
            
        logger.info(f"Filtered to {len(filtered_data)} stocks meeting quality criteria")
        return filtered_data
            
    def split_data_chronologically(self, df: pd.DataFrame, 
                                 train_ratio: float = 0.6,
                                 val_ratio: float = 0.2,
                                 test_ratio: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data chronologically into train/validation/test sets
        
        Args:
            df: Input DataFrame
            train_ratio: Training set proportion (default: 0.6)
            val_ratio: Validation set proportion (default: 0.2)
            test_ratio: Test set proportion (default: 0.2)
            
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
            raise ValueError("Ratios must sum to 1.0")
            
        # Get symbol for logging (if available)
        symbol = df['symbol'].iloc[0] if 'symbol' in df.columns and not df.empty else 'unknown'
        
        # Log input data characteristics
        if not df.empty:
            date_range_days = (df['trading_date_local'].max() - df['trading_date_local'].min()).days
            date_range_years = date_range_days / 365.25
            logger.info(f"📊 Time series split for {symbol}: {len(df)} records over {date_range_years:.1f} years ({date_range_days} days)")
            logger.info(f"   Date range: {df['trading_date_local'].min().date()} to {df['trading_date_local'].max().date()}")
            logger.info(f"   Split ratios: Train {train_ratio:.1%}, Val {val_ratio:.1%}, Test {test_ratio:.1%}")
        else:
            logger.warning(f"⚠️  Empty DataFrame provided for chronological split ({symbol})")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
        # Sort by date to ensure chronological order
        df_sorted = df.sort_values('trading_date_local').reset_index(drop=True)
        
        n = len(df_sorted)
        train_size = int(train_ratio * n)
        val_size = int(val_ratio * n)
        test_size = n - train_size - val_size  # Ensure all records are accounted for
        
        train_df = df_sorted.iloc[:train_size].copy()
        val_df = df_sorted.iloc[train_size:train_size + val_size].copy()
        test_df = df_sorted.iloc[train_size + val_size:].copy()
        
        # Log split results with detailed information
        logger.info(f"✅ Time series split completed for {symbol}:")
        logger.info(f"   📈 Train: {len(train_df)} records ({len(train_df)/n:.1%}) | {train_df['trading_date_local'].min().date()} to {train_df['trading_date_local'].max().date()}")
        logger.info(f"   📊 Val:   {len(val_df)} records ({len(val_df)/n:.1%}) | {val_df['trading_date_local'].min().date()} to {val_df['trading_date_local'].max().date()}")
        logger.info(f"   📋 Test:  {len(test_df)} records ({len(test_df)/n:.1%}) | {test_df['trading_date_local'].min().date()} to {test_df['trading_date_local'].max().date()}")
        
        # Verify no data leakage (chronological order)
        if (not train_df.empty and not val_df.empty and 
            train_df['trading_date_local'].max() >= val_df['trading_date_local'].min()):
            logger.warning(f"⚠️  Potential data leakage detected in {symbol}: Train max date >= Val min date")
            
        if (not val_df.empty and not test_df.empty and 
            val_df['trading_date_local'].max() >= test_df['trading_date_local'].min()):
            logger.warning(f"⚠️  Potential data leakage detected in {symbol}: Val max date >= Test min date")
            
        # Verify split integrity
        total_split_records = len(train_df) + len(val_df) + len(test_df)
        if total_split_records != n:
            logger.error(f"❌ Split integrity check failed for {symbol}: {total_split_records} != {n}")
        else:
            logger.debug(f"✅ Split integrity verified for {symbol}: {total_split_records} == {n}")
        
        return train_df, val_df, test_df
        
    def split_all_stocks_data(self, all_data: Dict[str, pd.DataFrame],
                            train_ratio: float = 0.6,
                            val_ratio: float = 0.2,
                            test_ratio: float = 0.2) -> Dict[str, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]:
        """
        Split data for all stocks chronologically
        
        Args:
            all_data: Dictionary of stock DataFrames
            train_ratio: Training set proportion
            val_ratio: Validation set proportion  
            test_ratio: Test set proportion
            
        Returns:
            Dictionary mapping symbol -> (train_df, val_df, test_df)
        """
        split_data = {}
        
        logger.info(f"🔄 Starting chronological data splits for {len(all_data)} stocks")
        
        for symbol, df in all_data.items():
            try:
                train_df, val_df, test_df = self.split_data_chronologically(
                    df, train_ratio, val_ratio, test_ratio
                )
                split_data[symbol] = (train_df, val_df, test_df)
                
            except Exception as e:
                logger.error(f"❌ Failed to split data for {symbol}: {e}")
                continue
                
        logger.info(f"✅ Completed chronological splits for {len(split_data)}/{len(all_data)} stocks")
                
        return split_data
        
    def get_data_summary(self, df: pd.DataFrame) -> dict:
        """Get summary statistics of the extracted data"""
        if df.empty:
            return {'error': 'Empty DataFrame'}
            
        summary = {
            'symbol': df['symbol'].iloc[0],
            'currency': df['currency'].iloc[0],
            'total_records': len(df),
            'date_range': {
                'start': df['trading_date_local'].min().date(),
                'end': df['trading_date_local'].max().date(),
                'days': (df['trading_date_local'].max() - df['trading_date_local'].min()).days
            },
            'price_stats': {
                'min': float(df['close_price'].min()),
                'max': float(df['close_price'].max()),
                'mean': float(df['close_price'].mean()),
                'std': float(df['close_price'].std())
            },
            'volume_stats': {
                'min': float(df['volume'].min()),
                'max': float(df['volume'].max()),
                'mean': float(df['volume'].mean()),
                'std': float(df['volume'].std())
            }
        }
        
        return summary
        
    def get_all_stocks_summary(self, all_data: Dict[str, pd.DataFrame]) -> Dict[str, dict]:
        """Get summary for all stocks"""
        summaries = {}
        for symbol, df in all_data.items():
            summaries[symbol] = self.get_data_summary(df)
        return summaries
        
    def close(self):
        """Close database connection"""
        if self.pg_conn:
            self.pg_conn.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    # Example usage
    extractor = MultiStockDataExtractor()
    
    try:
        # Get all available stocks
        available_stocks = extractor.get_available_stocks()
        print(f"Available stocks: {available_stocks}")
        
        # Extract data for all stocks
        all_data = extractor.extract_all_stocks_data()
        print(f"Extracted data for {len(all_data)} stocks")
        
        # Filter by quality criteria
        quality_data = extractor.filter_stocks_by_data_quality(
            all_data, 
            min_records=500,  # At least 500 trading days (~2 years)
            min_years=2.0     # At least 2 years of data
        )
        
        # Get summaries
        summaries = extractor.get_all_stocks_summary(quality_data)
        for symbol, summary in summaries.items():
            print(f"\n{symbol}: {summary['total_records']} records, "
                  f"{summary['date_range']['start']} to {summary['date_range']['end']}")
            
        # Split all stocks data
        if quality_data:
            split_data = extractor.split_all_stocks_data(quality_data)
            print(f"\nSplit data for {len(split_data)} stocks")
            
            # Example: Focus on XTB for testing
            if 'XTB' in split_data:
                train_df, val_df, test_df = split_data['XTB']
                print(f"\nXTB splits - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        extractor.close()