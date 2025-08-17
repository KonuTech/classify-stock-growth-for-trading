"""Command-line interface for stock ETL operations."""

import click
import sys
from pathlib import Path
from typing import Dict
import structlog
from datetime import datetime

from .core.database import get_database_manager, get_dev_database, get_test_database
from .core.models import InstrumentType, JobStatus
from .data.stooq_extractor import StooqExtractor, get_polish_market_symbols
from .database.operations import DatabaseOperations

# Configure structured logging with file output
import logging
from pathlib import Path

# Create logs directory
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure Python logging to write to file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "etl_debug.log"),
        logging.StreamHandler()  # Also keep console output
    ]
)

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(verbose):
    """Stock ETL Pipeline CLI."""
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    else:
        import logging
        logging.basicConfig(level=logging.INFO)


@main.group()
def database():
    """Database management commands."""
    pass


@database.command('test-connection')
@click.option('--schema', default='test_stock_data', help='Database schema to test')
def test_db_connection(schema):
    """Test database connectivity."""
    try:
        db_manager = get_database_manager(schema)
        if db_manager.test_connection():
            click.echo(f"✅ Database connection successful (schema: {schema})")
            return True
        else:
            click.echo(f"❌ Database connection failed (schema: {schema})")
            return False
    except Exception as e:
        click.echo(f"❌ Database connection error: {e}")
        return False


@database.command('init-dev')
def init_dev_database():
    """Initialize development database with dummy data."""
    try:
        click.echo("🚀 Initializing development database...")
        
        db_manager = get_dev_database()
        
        # Execute schema creation
        schema_file = Path("sql/01_dev_schema_normalized.sql")
        if not schema_file.exists():
            click.echo(f"❌ Schema file not found: {schema_file}")
            return False
        
        click.echo("📝 Creating development schema...")
        if not db_manager.execute_sql_file(str(schema_file)):
            click.echo("❌ Failed to create development schema")
            return False
        
        # Execute dummy data insertion
        data_file = Path("sql/02_dev_dummy_data.sql")
        if not data_file.exists():
            click.echo(f"❌ Data file not found: {data_file}")
            return False
        
        click.echo("📊 Inserting dummy data...")
        if not db_manager.execute_sql_file(str(data_file)):
            click.echo("❌ Failed to insert dummy data")
            return False
        
        click.echo("✅ Development database initialized successfully!")
        return True
        
    except Exception as e:
        click.echo(f"❌ Failed to initialize development database: {e}")
        return False


@database.command('init-test')
def init_test_database():
    """Initialize test database (clean, no dummy data)."""
    try:
        click.echo("🚀 Initializing test database...")
        
        db_manager = get_test_database()
        
        # Execute schema creation
        schema_file = Path("sql/03_test_schema_normalized.sql")
        if not schema_file.exists():
            click.echo(f"❌ Schema file not found: {schema_file}")
            return False
        
        click.echo("📝 Creating test schema...")
        if not db_manager.execute_sql_file(str(schema_file)):
            click.echo("❌ Failed to create test schema")
            return False
        
        click.echo("✅ Test database initialized successfully!")
        return True
        
    except Exception as e:
        click.echo(f"❌ Failed to initialize test database: {e}")
        return False


@main.group()
def extract():
    """Data extraction commands."""
    pass


@extract.command('sample')
@click.option('--output-dir', '-o', default='data', help='Output directory for downloaded files')
@click.option('--delay', '-d', default=2.0, help='Delay between requests (seconds)')
def extract_sample_data(output_dir, delay):
    """Extract sample Polish market data from Stooq."""
    try:
        click.echo("🔄 Extracting sample data from Stooq...")
        
        output_path = Path(output_dir)
        symbols = get_polish_market_symbols()
        
        click.echo(f"📊 Symbols to extract: {list(symbols.keys())}")
        click.echo(f"💾 Output directory: {output_path}")
        
        extractor = StooqExtractor()
        results = extractor.extract_multiple_symbols(
            symbols=symbols,
            save_directory=output_path,
            delay_between_requests=delay
        )
        extractor.close()
        
        # Summary
        successful = sum(1 for records in results.values() if records)
        total_records = sum(len(records) for records in results.values())
        
        click.echo(f"✅ Extraction completed!")
        click.echo(f"   Symbols processed: {len(symbols)}")
        click.echo(f"   Successful extractions: {successful}")
        click.echo(f"   Total records: {total_records}")
        
        return True
        
    except Exception as e:
        click.echo(f"❌ Failed to extract sample data: {e}")
        return False


@extract.command('symbol')
@click.argument('symbol')
@click.option('--type', 'instrument_type', 
              type=click.Choice(['stock', 'index']), 
              required=True, 
              help='Instrument type')
@click.option('--output-dir', '-o', default='data', help='Output directory')
def extract_single_symbol(symbol, instrument_type, output_dir):
    """Extract data for a single symbol."""
    try:
        click.echo(f"🔄 Extracting {instrument_type} data for {symbol}...")
        
        output_path = Path(output_dir)
        inst_type = InstrumentType.STOCK if instrument_type == 'stock' else InstrumentType.INDEX
        
        extractor = StooqExtractor()
        records = extractor.extract_symbol(symbol, inst_type, output_path)
        extractor.close()
        
        if records:
            click.echo(f"✅ Successfully extracted {len(records)} records for {symbol}")
            click.echo(f"   Date range: {records[-1].trading_date} to {records[0].trading_date}")
        else:
            click.echo(f"❌ No data extracted for {symbol}")
        
        return len(records) > 0
        
    except Exception as e:
        click.echo(f"❌ Failed to extract data for {symbol}: {e}")
        return False


@main.group()
def load():
    """Data loading commands."""
    pass


@load.command('sample')
@click.option('--schema', default='test_stock_data', help='Target database schema')
def load_sample_data(schema):
    """Load sample data into database."""
    try:
        click.echo(f"🔄 Loading sample data into {schema} schema...")
        
        # First extract the data
        click.echo("📥 Extracting fresh data from Stooq...")
        symbols = get_polish_market_symbols()
        
        extractor = StooqExtractor()
        results = extractor.extract_multiple_symbols(
            symbols=symbols,
            save_directory=None,  # Don't save to files
            delay_between_requests=1.5
        )
        extractor.close()
        
        if not any(results.values()):
            click.echo("❌ No data extracted from Stooq")
            return False
        
        # Load into database
        click.echo("💾 Loading data into database...")
        db_ops = DatabaseOperations(schema)
        
        with db_ops.get_db_session(schema) as session:
            # Create ETL job
            job_id = db_ops.create_etl_job(
                session,
                job_name=f"sample_data_load_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                job_type="sample_data_load",
                target_instrument_type=None
            )
            
            total_processed = total_inserted = total_failed = 0
            
            for symbol, records in results.items():
                if not records:
                    continue
                
                instrument_type = symbols[symbol]
                click.echo(f"   Processing {symbol} ({instrument_type.value}): {len(records)} records")
                
                processed, inserted, failed = db_ops.process_symbol_data(
                    session, symbol, instrument_type, records, job_id
                )
                
                total_processed += processed
                total_inserted += inserted
                total_failed += failed
                
                session.commit()  # Commit after each symbol
            
            # Update job status
            final_status = JobStatus.COMPLETED if total_failed == 0 else JobStatus.FAILED
            db_ops.update_etl_job_status(
                session, job_id, final_status,
                records_processed=total_processed,
                records_inserted=total_inserted,
                records_failed=total_failed
            )
            
            session.commit()
        
        click.echo(f"✅ Data loading completed!")
        click.echo(f"   Total records processed: {total_processed}")
        click.echo(f"   Successfully inserted: {total_inserted}")
        click.echo(f"   Failed: {total_failed}")
        click.echo(f"   ETL Job ID: {job_id}")
        
        return total_failed == 0
        
    except Exception as e:
        click.echo(f"❌ Failed to load sample data: {e}")
        return False


@load.command('symbol')
@click.argument('symbol')
@click.option('--type', 'instrument_type', 
              type=click.Choice(['stock', 'index']), 
              required=True, 
              help='Instrument type')
@click.option('--schema', default='test_stock_data', help='Target database schema')
def load_single_symbol(symbol, instrument_type, schema):
    """Load data for a single symbol into database."""
    try:
        click.echo(f"🔄 Loading {instrument_type} data for {symbol} into {schema}...")
        
        # Extract data
        inst_type = InstrumentType.STOCK if instrument_type == 'stock' else InstrumentType.INDEX
        
        extractor = StooqExtractor()
        records = extractor.extract_symbol(symbol, inst_type)
        extractor.close()
        
        if not records:
            click.echo(f"❌ No data extracted for {symbol}")
            return False
        
        # Load into database
        db_ops = DatabaseOperations(schema)
        
        with db_ops.get_db_session(schema) as session:
            # Create ETL job
            job_id = db_ops.create_etl_job(
                session,
                job_name=f"single_symbol_load_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                job_type="single_symbol_load",
                target_instrument_type=inst_type
            )
            
            processed, inserted, failed = db_ops.process_symbol_data(
                session, symbol, inst_type, records, job_id
            )
            
            # Update job status
            final_status = JobStatus.COMPLETED if failed == 0 else JobStatus.FAILED
            db_ops.update_etl_job_status(
                session, job_id, final_status,
                records_processed=processed,
                records_inserted=inserted,
                records_failed=failed
            )
            
            session.commit()
        
        click.echo(f"✅ Loading completed!")
        click.echo(f"   Records processed: {processed}")
        click.echo(f"   Successfully inserted: {inserted}")
        click.echo(f"   Failed: {failed}")
        click.echo(f"   ETL Job ID: {job_id}")
        
        return failed == 0
        
    except Exception as e:
        click.echo(f"❌ Failed to load data for {symbol}: {e}")
        return False


@main.command('pipeline')
@click.option('--schema', default='test_stock_data', help='Target database schema')
def run_full_pipeline(schema):
    """Run the complete ETL pipeline."""
    try:
        click.echo("🚀 Running full ETL pipeline...")
        
        # Step 1: Test database connection
        click.echo("1️⃣ Testing database connection...")
        if not test_db_connection.callback(schema):
            return False
        
        # Step 2: Initialize database if needed
        if schema == 'test_stock_data':
            click.echo("2️⃣ Initializing test database...")
            if not init_test_database.callback():
                return False
        
        # Step 3: Load sample data
        click.echo("3️⃣ Loading sample data...")
        if not load_sample_data.callback(schema):
            return False
        
        click.echo("🎉 Full ETL pipeline completed successfully!")
        return True
        
    except Exception as e:
        click.echo(f"❌ Pipeline failed: {e}")
        return False


if __name__ == '__main__':
    main()