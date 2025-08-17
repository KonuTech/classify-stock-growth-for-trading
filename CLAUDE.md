# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a stock data ETL pipeline project that extracts financial data from Stooq, stores it in a normalized PostgreSQL database, and provides Apache Airflow integration for orchestration. The project follows a normalized database design with proper data validation and structured logging.

## Core Architecture

### Database Design
- **Normalized schema** with separate tables for exchanges, instruments, stocks, indices, and price data
- **Multi-schema support**: `dev_stock_data`, `test_stock_data`, `stock_data_test`
- **Timezone-aware**: Stores both local and UTC timestamps with epoch support
- **Data integrity**: Comprehensive constraints and validation at database level

### Key Components
- **stock_etl.core.models**: Pydantic models for validation and type safety
- **stock_etl.core.database**: Database connection management with pooling
- **stock_etl.data.stooq_extractor**: Data extraction from Stooq financial service
- **stock_etl.database.operations**: Database CRUD operations for normalized schema
- **stock_etl.cli**: Command-line interface for all ETL operations
- **stock_etl.airflow_dags.stock_etl_dag**: Unified Airflow DAG with comprehensive workflow
- **stock_etl.utils.dag_utils**: DAG utilities for execution mode detection and logging
- **stock_etl.utils.polish_trading_calendar**: Warsaw Stock Exchange trading calendar

### Data Flow
1. Extract data from Stooq API (CSV format)
2. Validate using Pydantic models (StooqRecord)
3. Transform and load into normalized PostgreSQL tables
4. Track ETL jobs and data quality metrics

## Essential Commands

### Development Setup
```bash
# Install dependencies
uv sync

# Install with development dependencies
uv sync --group dev

# Start PostgreSQL and Airflow services
docker-compose up -d

# Initialize development database with dummy data
stock-etl database init-dev

# Initialize clean test database
stock-etl database init-test

# Test database connectivity
stock-etl database test-connection --schema stock_data_test
```

### ETL Operations
```bash
# Extract sample Polish market data
stock-etl extract sample --output-dir data --delay 2.0

# Extract single symbol
stock-etl extract symbol XTB --type stock --output-dir data

# Load sample data into database
stock-etl load sample --schema stock_data_test

# Load single symbol
stock-etl load symbol XTB --type stock --schema stock_data_test

# Run complete ETL pipeline
stock-etl pipeline --schema stock_data_test
```

### Code Quality
```bash
# Format code
black stock_etl/ tests/

# Lint code
ruff check stock_etl/ tests/

# Type checking
mypy stock_etl/

# Run tests (basic test file available)
python test_etl.py

# Run tests with pytest (if tests/ directory is populated)
pytest tests/ -v --cov=stock_etl
```

## Database Schemas

### Schema Structure
- **exchanges**: WSE, NewConnect, etc.
- **base_instruments**: Common instrument data (symbol, name, type)
- **stocks**: Stock-specific data (company_name, sector)
- **indices**: Index-specific data (methodology, base_value)
- **stock_prices**: Daily OHLCV data for stocks
- **index_prices**: Daily OHLCV data for indices
- **etl_jobs**: Job tracking and monitoring
- **data_quality_metrics**: Automated data validation results

### Schema Initialization Files
- `sql/01_dev_schema_normalized.sql`: Development schema with dummy data
- `sql/02_dev_dummy_data.sql`: Sample data for development
- `sql/03_test_schema_normalized.sql`: Clean test schema

## Environment Configuration

### Database Connection
Set these environment variables or use defaults:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_data
DB_USER=postgres
DB_PASSWORD=postgres
```

### Docker Services
- PostgreSQL: Available on port 5432
- Airflow Webserver: Available on port 8080 (admin/u8Zt2hYnsqXM4MNw)
- Airflow uses LocalExecutor with PostgreSQL backend

### Docker Management
```bash
# View service logs
docker-compose logs -f postgres
docker-compose logs -f airflow

# Restart services
docker-compose restart

# Stop and remove all containers/volumes (full reset)
docker-compose down -v
```

## Airflow Integration

### Unified DAG Architecture
The `stock_etl_unified_pipeline` DAG in `stock_etl/airflow_dags/stock_etl_dag.py` provides:

- **Smart Execution Mode Detection**: Automatically detects backfill vs incremental runs
- **Polish Trading Calendar Integration**: Uses `polish_trading_calendar.py` for market day validation
- **Comprehensive ETL Job Tracking**: Full lifecycle tracking with Airflow context
- **Data Quality Validation**: Automated OHLC validation and anomaly detection
- **Error Handling and Retry Logic**: Graceful failure handling with detailed logging

### DAG Configuration Parameters
```python
# Default DAG parameters (configurable via Airflow UI)
{
    "schema": "prod_stock_data",      # Target database schema
    "mode": "incremental",           # incremental | backfill
    "instruments": "all",            # all | specific symbols
    "data_sources": "stooq",         # Data source configuration
    "enable_validation": true,       # Enable data quality checks
    "batch_size": 50                 # Processing batch size
}
```

### DAG Task Flow
1. **check_prerequisites** - Validates trading calendar and execution context
2. **create_etl_job** - Creates ETL job record with comprehensive metadata
3. **extract_and_transform** - Data extraction with source tracking
4. **load_data** - Database loading with detailed per-instrument tracking
5. **validate_data_quality** - Automated quality checks (OHLC, gaps, volumes)
6. **finalize_etl_session** - Job completion with final status and metrics

### Manual DAG Operations
```bash
# Trigger DAG via Airflow CLI
docker-compose exec airflow airflow dags trigger stock_etl_unified_pipeline \
  --conf '{"schema": "dev_stock_data", "mode": "incremental"}'

# Test specific date (backfill)
docker-compose exec airflow airflow dags test stock_etl_unified_pipeline "2025-08-15" \
  --conf '{"schema": "dev_stock_data", "mode": "backfill"}'

# List DAG runs
docker-compose exec airflow airflow dags list-runs -d stock_etl_unified_pipeline

# Check DAG status and next runs
docker-compose exec airflow airflow dags show stock_etl_unified_pipeline

# Monitor task logs
docker-compose exec airflow airflow tasks logs stock_etl_unified_pipeline extract_and_transform 2025-08-17

# Clear DAG run for retry
docker-compose exec airflow airflow dags clear -c stock_etl_unified_pipeline
```

### ETL Job Monitoring
```bash
# Connect to database and check ETL jobs
docker-compose exec postgres psql -U postgres -d stock_data

# Monitor recent ETL jobs
SET search_path TO dev_stock_data;
SELECT job_name, status, records_processed, duration_seconds, started_at 
FROM etl_jobs 
ORDER BY started_at DESC LIMIT 10;

# Check data quality metrics
SELECT instrument_id, metric_name, is_valid, severity 
FROM data_quality_metrics 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days' 
  AND is_valid = FALSE;
```

## Data Sources and Formats

### Stooq Integration
- **Base URL**: https://stooq.com/q/d/l/
- **Format**: CSV with columns: Date,Open,High,Low,Close,Volume
- **Rate Limiting**: 1-2 second delays between requests
- **Supported Markets**: Polish Stock Exchange (WSE)

### Predefined Symbols
**Stocks**: XTB, PKN, CCC, LPP, CDR  
**Indices**: WIG, WIG20, MWIG40, SWIG80

## Logging and Monitoring

### Structured Logging
- Uses `structlog` with JSON output
- Logs written to `logs/etl_debug.log`
- Different log levels for development vs production

### ETL Job Tracking
- All operations tracked in `etl_jobs` table
- Detailed metrics: records processed, inserted, failed
- Integration with Airflow DAG and task IDs

## Testing Approach

### Test Database
- Use `stock_data_test` schema for testing
- Clean initialization without dummy data
- Isolated from development data

### Validation Strategy
- Pydantic models validate all input data
- OHLC price relationship validation
- Database constraints enforce data integrity
- Hash-based duplicate detection

## Key Design Patterns

### Database Operations
- Connection pooling with SQLAlchemy
- Context managers for session management
- Raw SQL for performance-critical operations
- Schema-aware search path configuration

### Error Handling
- Comprehensive logging at all levels
- Graceful degradation for data extraction failures
- Retry logic with exponential backoff
- Detailed error tracking in ETL jobs

### Data Validation
- Multi-layer validation: Pydantic → Database → Business rules
- Automatic type conversion and cleaning
- Price relationship validation (high ≥ open/close ≥ low)
- Trading date and volume validation

## Trading Calendar & DAG Utilities

### Polish Trading Calendar (`polish_trading_calendar.py`)
- **WSE Trading Hours**: 9:00-17:00 CET/CEST, Monday-Friday
- **Holiday Integration**: Uses `holidays` library for Polish public holidays
- **Smart Date Functions**: 
  - `is_trading_day()` - Validates trading days excluding weekends/holidays
  - `get_previous_trading_day()` - For incremental ETL target date calculation
  - `get_trading_days_in_range()` - For backfill operations
  - `is_market_open_now()` - Real-time market status

### DAG Utilities (`dag_utils.py`)
- **Execution Mode Detection**: Automatically determines backfill vs incremental based on:
  - DAG run type (manual, backfill, scheduled)
  - Execution date age (>7 days = backfill)
  - Explicit configuration parameters
- **ETL Logger**: Enhanced logging with file and console handlers for Airflow
- **Schema Context Management**: Dynamic schema selection from DAG parameters
- **Date Range Validation**: Prevents accidentally huge backfill operations

### Trading Calendar Logic
```python
# Incremental mode: Process previous trading day
target_date = polish_calendar.get_previous_trading_day(today)

# Backfill mode: Process exact execution date (if trading day)
if not polish_calendar.is_trading_day(execution_date):
    # Skip non-trading days or log warning
```

## Schema Management

### Jinja2 Template System (`sql/schema_template.sql.j2`)
Dynamic schema generation supporting multiple environments:

- **Template Variables**: `schema_name`, `schema_type` (dev/test/prod)
- **Environment-Specific Data**: Test schemas exclude dummy data
- **Comprehensive Schema**: All tables, indexes, functions, and triggers
- **Performance Optimization**: Automatically creates optimized indexes

### Schema Types and Usage
```bash
# Development schema with dummy data
schema_type: "development" → Includes sample instruments and test data

# Test schema - clean environment  
schema_type: "test" → Reference data only, no dummy prices

# Production schema
schema_type: "production" → Production-ready with full constraints
```

### Key Schema Features
- **Normalized Design**: Separate tables for exchanges, instruments, stocks, indices
- **Timezone Support**: UTC and local timestamps with epoch conversion
- **Data Integrity**: OHLC validation, positive price constraints
- **Performance Indexes**: Optimized for time-series queries and joins
- **ETL Tracking**: Complete job lifecycle and data quality metrics