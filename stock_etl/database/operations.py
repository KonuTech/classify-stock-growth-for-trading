"""Database operations for normalized schema."""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import structlog

from ..core.models import (
    StooqRecord, BaseInstrument, StockData, IndexData, 
    StockPrice, IndexPrice, ETLJob, ETLJobDetail, DataQualityMetric,
    InstrumentType, JobStatus, SeverityLevel
)
from ..core.database import get_db_session

logger = structlog.get_logger(__name__)


class DatabaseOperations:
    """Database operations for the normalized schema."""
    
    def __init__(self, schema: str = "stock_data_test"):
        self.schema = schema
    
    def get_db_session(self, schema: str):
        """Get database session for the specified schema."""
        return get_db_session(schema)
    
    def get_or_create_exchange(self, session: Session, exchange_name: str = "WSE") -> int:
        """Get or create exchange, return exchange_id."""
        try:
            result = session.execute(
                text("SELECT id FROM exchanges WHERE mic_code = :mic_code"),
                {"mic_code": "XWAR" if exchange_name == "WSE" else exchange_name}
            ).fetchone()
            
            if result:
                return result[0]
            
            # For now, assume WSE exists (created by schema initialization)
            logger.warning("Exchange not found, using default", exchange_name=exchange_name)
            return 1  # Default WSE exchange_id
            
        except Exception as e:
            logger.error("Failed to get exchange", exchange_name=exchange_name, error=str(e))
            raise
    
    def get_or_create_sector(self, session: Session, sector_name: str) -> Optional[int]:
        """Get or create sector, return sector_id."""
        try:
            result = session.execute(
                text("SELECT id FROM sectors WHERE name = :name"),
                {"name": sector_name}
            ).fetchone()
            
            if result:
                return result[0]
            
            # Create new sector
            result = session.execute(
                text("""
                    INSERT INTO sectors (name, description, classification_system)
                    VALUES (:name, :description, 'GICS')
                    RETURNING id
                """),
                {"name": sector_name, "description": f"Auto-created sector: {sector_name}"}
            )
            sector_id = result.fetchone()[0]
            logger.info("Created new sector", sector_name=sector_name, sector_id=sector_id)
            return sector_id
            
        except Exception as e:
            logger.error("Failed to get/create sector", sector_name=sector_name, error=str(e))
            return None
    
    def create_base_instrument(
        self, 
        session: Session, 
        symbol: str, 
        name: str, 
        instrument_type: InstrumentType,
        exchange_id: int,
        first_trading_date: Optional[date] = None
    ) -> int:
        """Create base instrument record, return instrument_id."""
        try:
            result = session.execute(
                text("""
                    INSERT INTO base_instruments 
                    (symbol, name, instrument_type, exchange_id, currency, is_active, first_trading_date)
                    VALUES (:symbol, :name, :instrument_type, :exchange_id, 'PLN', true, :first_trading_date)
                    ON CONFLICT (symbol, exchange_id) 
                    DO UPDATE SET 
                        name = EXCLUDED.name,
                        instrument_type = EXCLUDED.instrument_type,
                        first_trading_date = COALESCE(EXCLUDED.first_trading_date, base_instruments.first_trading_date),
                        updated_at = CURRENT_TIMESTAMP,
                        updated_at_epoch = EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT
                    RETURNING id
                """),
                {
                    "symbol": symbol.upper(),
                    "name": name,
                    "instrument_type": instrument_type.value,
                    "exchange_id": exchange_id,
                    "first_trading_date": first_trading_date
                }
            )
            
            instrument_id = result.fetchone()[0]
            logger.info("Created/updated base instrument", symbol=symbol, instrument_id=instrument_id)
            return instrument_id
            
        except Exception as e:
            logger.error("Failed to create base instrument", symbol=symbol, error=str(e))
            raise
    
    def create_stock(
        self, 
        session: Session, 
        instrument_id: int, 
        company_name: str,
        sector_name: Optional[str] = None
    ) -> int:
        """Create stock record, return stock_id."""
        try:
            sector_id = None
            if sector_name:
                sector_id = self.get_or_create_sector(session, sector_name)
            
            result = session.execute(
                text("""
                    INSERT INTO stocks (instrument_id, company_name, sector_id, stock_type)
                    VALUES (:instrument_id, :company_name, :sector_id, 'common')
                    ON CONFLICT (instrument_id) 
                    DO UPDATE SET 
                        company_name = EXCLUDED.company_name,
                        sector_id = COALESCE(EXCLUDED.sector_id, stocks.sector_id)
                    RETURNING id
                """),
                {
                    "instrument_id": instrument_id,
                    "company_name": company_name,
                    "sector_id": sector_id
                }
            )
            
            stock_id = result.fetchone()[0]
            logger.info("Created/updated stock", instrument_id=instrument_id, stock_id=stock_id)
            return stock_id
            
        except Exception as e:
            logger.error("Failed to create stock", instrument_id=instrument_id, error=str(e))
            raise
    
    def create_index(
        self, 
        session: Session, 
        instrument_id: int,
        base_value: Decimal = Decimal('1000.0'),
        base_date: Optional[date] = None
    ) -> int:
        """Create index record, return index_id."""
        try:
            if base_date is None:
                base_date = date(1991, 4, 16)  # Default WIG base date
            
            result = session.execute(
                text("""
                    INSERT INTO indices (instrument_id, methodology, base_value, base_date, calculation_frequency)
                    VALUES (:instrument_id, 'market_cap_weighted', :base_value, :base_date, 'real_time')
                    ON CONFLICT (instrument_id) 
                    DO UPDATE SET 
                        base_value = EXCLUDED.base_value,
                        base_date = EXCLUDED.base_date
                    RETURNING id
                """),
                {
                    "instrument_id": instrument_id,
                    "base_value": float(base_value),
                    "base_date": base_date
                }
            )
            
            index_id = result.fetchone()[0]
            logger.info("Created/updated index", instrument_id=instrument_id, index_id=index_id)
            return index_id
            
        except Exception as e:
            logger.error("Failed to create index", instrument_id=instrument_id, error=str(e))
            raise
    
    def get_instrument_info(self, session: Session, symbol: str) -> Optional[Dict[str, Any]]:
        """Get existing instrument information."""
        try:
            result = session.execute(
                text("""
                    SELECT 
                        bi.id as instrument_id,
                        bi.symbol,
                        bi.instrument_type,
                        bi.exchange_id,
                        s.id as stock_id,
                        i.id as index_id
                    FROM base_instruments bi
                    LEFT JOIN stocks s ON bi.id = s.instrument_id
                    LEFT JOIN indices i ON bi.id = i.instrument_id
                    WHERE bi.symbol = :symbol
                    LIMIT 1
                """),
                {"symbol": symbol.upper()}
            ).fetchone()
            
            if result:
                return {
                    "instrument_id": result[0],
                    "symbol": result[1],
                    "instrument_type": result[2],
                    "exchange_id": result[3],
                    "stock_id": result[4],
                    "index_id": result[5]
                }
            return None
            
        except Exception as e:
            logger.error("Failed to get instrument info", symbol=symbol, error=str(e))
            return None
    
    def calculate_epoch_timestamp(self, trading_date: date, timezone_name: str = "Europe/Warsaw") -> int:
        """Calculate epoch timestamp for a trading date."""
        import pytz
        tz = pytz.timezone(timezone_name)
        # Assume market close time for the epoch calculation
        dt = datetime.combine(trading_date, datetime.min.time().replace(hour=17, minute=30))
        localized_dt = tz.localize(dt)
        return int(localized_dt.timestamp())
    
    def insert_stock_price(
        self, 
        session: Session, 
        stock_id: int, 
        record: StooqRecord
    ) -> bool:
        """Insert stock price record."""
        try:
            trading_date_epoch = self.calculate_epoch_timestamp(record.trading_date)
            
            session.execute(
                text("""
                    INSERT INTO stock_prices (
                        stock_id, trading_date_local, trading_date_utc, trading_date_epoch,
                        open_price, high_price, low_price, close_price, volume,
                        adjusted_close, data_source, raw_data_hash
                    ) VALUES (
                        :stock_id, :trading_date, :trading_date, :trading_date_epoch,
                        :open_price, :high_price, :low_price, :close_price, :volume,
                        :close_price, 'stooq', :raw_data_hash
                    )
                    ON CONFLICT (stock_id, trading_date_local) 
                    DO UPDATE SET 
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume,
                        adjusted_close = EXCLUDED.adjusted_close,
                        raw_data_hash = EXCLUDED.raw_data_hash
                """),
                {
                    "stock_id": stock_id,
                    "trading_date": record.trading_date,
                    "trading_date_epoch": trading_date_epoch,
                    "open_price": float(record.open_price),
                    "high_price": float(record.high_price),
                    "low_price": float(record.low_price),
                    "close_price": float(record.close_price),
                    "volume": int(record.volume),
                    "raw_data_hash": record.calculate_hash()
                }
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to insert stock price",
                stock_id=stock_id,
                date=record.trading_date,
                error=str(e)
            )
            return False
    
    def insert_index_price(
        self, 
        session: Session, 
        index_id: int, 
        record: StooqRecord
    ) -> bool:
        """Insert index price record."""
        try:
            trading_date_epoch = self.calculate_epoch_timestamp(record.trading_date)
            
            session.execute(
                text("""
                    INSERT INTO index_prices (
                        index_id, trading_date_local, trading_date_utc, trading_date_epoch,
                        open_value, high_value, low_value, close_value, trading_volume,
                        data_source, raw_data_hash
                    ) VALUES (
                        :index_id, :trading_date, :trading_date, :trading_date_epoch,
                        :open_value, :high_value, :low_value, :close_value, :trading_volume,
                        'stooq', :raw_data_hash
                    )
                    ON CONFLICT (index_id, trading_date_local) 
                    DO UPDATE SET 
                        open_value = EXCLUDED.open_value,
                        high_value = EXCLUDED.high_value,
                        low_value = EXCLUDED.low_value,
                        close_value = EXCLUDED.close_value,
                        trading_volume = EXCLUDED.trading_volume,
                        raw_data_hash = EXCLUDED.raw_data_hash
                """),
                {
                    "index_id": index_id,
                    "trading_date": record.trading_date,
                    "trading_date_epoch": trading_date_epoch,
                    "open_value": float(record.open_price),
                    "high_value": float(record.high_price),
                    "low_value": float(record.low_price),
                    "close_value": float(record.close_price),
                    "trading_volume": int(record.volume),
                    "raw_data_hash": record.calculate_hash()
                }
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to insert index price",
                index_id=index_id,
                date=record.trading_date,
                error=str(e)
            )
            return False
    
    def create_etl_job(
        self, 
        session: Session,
        job_name: str,
        job_type: str,
        target_instrument_type: Optional[InstrumentType] = None,
        airflow_context: Optional[Dict[str, Any]] = None
    ) -> int:
        """Create ETL job record, return job_id."""
        try:
            params = {
                "job_name": job_name,
                "job_type": job_type,
                "target_instrument_type": target_instrument_type.value if target_instrument_type else None,
                "status": JobStatus.RUNNING.value,
                "started_at": datetime.now(timezone.utc),
                "started_at_epoch": int(datetime.now(timezone.utc).timestamp())
            }
            
            # Add Airflow context if provided
            if airflow_context:
                params.update({
                    "airflow_dag_id": airflow_context.get("dag_id"),
                    "airflow_task_id": airflow_context.get("task_id"),
                    "airflow_run_id": airflow_context.get("run_id"),
                    "metadata": airflow_context
                })
            
            result = session.execute(
                text("""
                    INSERT INTO etl_jobs (
                        job_name, job_type, target_instrument_type, status, 
                        started_at, started_at_epoch, airflow_dag_id, airflow_task_id, 
                        airflow_run_id, metadata
                    ) VALUES (
                        :job_name, :job_type, :target_instrument_type, :status,
                        :started_at, :started_at_epoch, :airflow_dag_id, :airflow_task_id,
                        :airflow_run_id, :metadata
                    ) RETURNING id
                """),
                params
            )
            
            job_id = result.fetchone()[0]
            logger.info("Created ETL job", job_name=job_name, job_id=job_id)
            return job_id
            
        except Exception as e:
            logger.error("Failed to create ETL job", job_name=job_name, error=str(e))
            raise
    
    def update_etl_job_status(
        self, 
        session: Session,
        job_id: int,
        status: JobStatus,
        records_processed: int = 0,
        records_inserted: int = 0,
        records_updated: int = 0,
        records_failed: int = 0,
        error_message: Optional[str] = None
    ) -> bool:
        """Update ETL job status and metrics."""
        try:
            params = {
                "job_id": job_id,
                "status": status.value,
                "records_processed": records_processed,
                "records_inserted": records_inserted,
                "records_updated": records_updated,
                "records_failed": records_failed,
                "error_message": error_message
            }
            
            if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                params.update({
                    "completed_at": datetime.now(timezone.utc),
                    "completed_at_epoch": int(datetime.now(timezone.utc).timestamp())
                })
            
            session.execute(
                text("""
                    UPDATE etl_jobs SET 
                        status = :status,
                        records_processed = :records_processed,
                        records_inserted = :records_inserted,
                        records_updated = :records_updated,
                        records_failed = :records_failed,
                        error_message = :error_message,
                        completed_at = COALESCE(:completed_at, completed_at),
                        completed_at_epoch = COALESCE(:completed_at_epoch, completed_at_epoch)
                    WHERE id = :job_id
                """),
                params
            )
            
            logger.info(
                "Updated ETL job status",
                job_id=job_id,
                status=status.value,
                records_processed=records_processed
            )
            return True
            
        except Exception as e:
            logger.error("Failed to update ETL job status", job_id=job_id, error=str(e))
            return False
    
    def process_symbol_data(
        self, 
        session: Session,
        symbol: str,
        instrument_type: InstrumentType,
        records: List[StooqRecord],
        job_id: int
    ) -> Tuple[int, int, int]:  # processed, inserted, failed
        """Process all records for a symbol."""
        processed = inserted = failed = 0
        
        try:
            # Get or create instrument
            instrument_info = self.get_instrument_info(session, symbol)
            
            if not instrument_info:
                # Create new instrument
                exchange_id = self.get_or_create_exchange(session, "WSE")
                first_trading_date = min(record.trading_date for record in records) if records else None
                
                instrument_id = self.create_base_instrument(
                    session, symbol, f"{symbol} - Auto-created", 
                    instrument_type, exchange_id, first_trading_date
                )
                
                # Create stock or index
                if instrument_type == InstrumentType.STOCK:
                    stock_id = self.create_stock(session, instrument_id, f"{symbol} Company")
                    index_id = None
                else:
                    index_id = self.create_index(session, instrument_id)
                    stock_id = None
                    
                instrument_info = {
                    "instrument_id": instrument_id,
                    "stock_id": stock_id,
                    "index_id": index_id,
                    "instrument_type": instrument_type.value
                }
            
            # Process price records
            for record in records:
                processed += 1
                
                try:
                    if instrument_type == InstrumentType.STOCK and instrument_info["stock_id"]:
                        success = self.insert_stock_price(session, instrument_info["stock_id"], record)
                    elif instrument_type == InstrumentType.INDEX and instrument_info["index_id"]:
                        success = self.insert_index_price(session, instrument_info["index_id"], record)
                    else:
                        logger.error("Invalid instrument configuration", symbol=symbol, instrument_info=instrument_info)
                        failed += 1
                        continue
                    
                    if success:
                        inserted += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    logger.error("Failed to process record", symbol=symbol, date=record.trading_date, error=str(e))
                    failed += 1
            
            # Log job detail
            session.execute(
                text("""
                    INSERT INTO etl_job_details (
                        job_id, instrument_id, symbol, operation, 
                        date_processed, date_processed_epoch, records_count
                    ) VALUES (
                        :job_id, :instrument_id, :symbol, 'bulk_insert',
                        :date_processed, :date_processed_epoch, :records_count
                    )
                """),
                {
                    "job_id": job_id,
                    "instrument_id": instrument_info["instrument_id"],
                    "symbol": symbol,
                    "date_processed": date.today(),
                    "date_processed_epoch": int(datetime.now(timezone.utc).timestamp()),
                    "records_count": inserted
                }
            )
            
            logger.info(
                "Processed symbol data",
                symbol=symbol,
                processed=processed,
                inserted=inserted,
                failed=failed
            )
            
        except Exception as e:
            logger.error("Failed to process symbol data", symbol=symbol, error=str(e))
            failed = processed
            inserted = 0
        
        return processed, inserted, failed