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

# Run tests
pytest tests/
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
- Airflow Webserver: Available on port 8080 (admin/admin)
- Airflow uses LocalExecutor with PostgreSQL backend

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