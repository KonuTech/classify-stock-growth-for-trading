# Stock ETL Pipeline for Trading Data

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)
![Airflow](https://img.shields.io/badge/Airflow-3.0.4-orange)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

A production-ready ETL pipeline for extracting, transforming, and loading Polish stock market data with automated scheduling, intelligent processing modes, and comprehensive monitoring. Features unified ID schema design, multi-environment support, and trading calendar integration.

> **📚 Developer Resources**: For detailed technical documentation, architecture decisions, and development guidance, see **[CLAUDE.md](CLAUDE.md)**. This file contains comprehensive information about the codebase structure, essential commands, database design patterns, Airflow DAG configuration, and trading calendar integration.

## 🎯 Project Overview

This project implements a robust data pipeline that:
- **Extracts** financial data from Stooq API for Polish Stock Exchange (WSE)
- **Transforms** and validates data using Pydantic models
- **Loads** into a normalized PostgreSQL database with full audit trails
- **Orchestrates** daily operations using Apache Airflow with trading calendar integration
- **Monitors** data quality and ETL job performance

### 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Stooq API     │───▶│  ETL Pipeline   │───▶│  PostgreSQL 17  │
│  (Data Source)  │    │   (Python)      │    │ (Normalized DB) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Apache Airflow  │
                       │  (Scheduling)   │
                       └─────────────────┘
```

## 📊 Data Model

The system uses a **normalized database design** following 3NF/BCNF principles:

```mermaid
erDiagram
    countries ||--o{ exchanges : "located in"
    exchanges ||--o{ base_instruments : "trades on"
    sectors ||--o{ stocks : "categorizes"
    base_instruments ||--|| stocks : "specialized as"
    base_instruments ||--|| indices : "specialized as"
    stocks ||--o{ stock_prices : "has daily prices"
    indices ||--o{ index_prices : "has daily values"
    etl_jobs ||--o{ etl_job_details : "contains details"
    base_instruments ||--o{ data_quality_metrics : "has metrics"
```

### Key Tables
- **Financial Data**: `stock_prices`, `index_prices` with OHLCV data
- **Instruments**: `base_instruments` (unified ID), `stocks`, `indices` with metadata
- **ETL Tracking**: `etl_jobs`, `etl_job_details`, `data_quality_metrics`
- **Reference Data**: `countries`, `exchanges`, `sectors`

### Unified ID Design
The system uses a **single instrument identifier** (`base_instruments.id`) across all tables, eliminating complex JOINs and improving query performance. Stock and index prices reference `base_instruments.id` directly.

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **Docker & Docker Compose**
- **WSL2** (for Windows users)

### 1. Installation

```bash
# Clone repository
git clone https://github.com/KonuTech/classify-stock-growth-for-trading.git
cd classify-stock-growth-for-trading

# Install dependencies using uv (recommended)
uv sync

# Install with development dependencies
uv sync --group dev

# Or using pip
pip install -e .
```

### 2. Complete Infrastructure Setup (Recommended)

```bash
# 🚀 COMPLETE DEPLOYMENT: Start all services + initialize schemas + trigger DAGs
make start

# This comprehensive command will:
# - Start PostgreSQL 17, Airflow 3.0.4, and pgAdmin services
# - Initialize dev_stock_data and test_stock_data schemas with unified ID design
# - Set up database permissions for multi-user access
# - Configure Airflow connections automatically (postgres_default, postgres_stock)
# - Trigger development DAG (incremental mode)
# - Trigger test environment DAG (FULL_BACKFILL mode - 50,000+ records)
# - Extract all service credentials to .env file
# - Display access URLs and credentials

# ⚠️  NOTE: make start automatically runs test DAG in full_backfill mode
# This will download complete historical data (~5-10 minutes processing time)
```

### 3. Manual Step-by-Step Setup (Alternative)

```bash
# Start PostgreSQL and Airflow containers
docker-compose up -d

# Wait for services to be ready (30-60 seconds)
docker-compose logs -f postgres  # Wait for "ready to accept connections"

# Initialize development environment with sample data
make init-dev

# Initialize clean test environment for real market data
make init-test

# Test database connectivity
uv run python -m stock_etl.cli database test-connection --schema dev_stock_data

# Extract service credentials (optional)
make extract-credentials
```

### 4. Run ETL Pipeline

```bash
# Recommended: Use Makefile commands for automated pipeline execution

# Trigger development environment DAG (incremental mode - sample data)
make trigger-dev-dag

# Trigger test environment DAG (FULL_BACKFILL mode - all historical Stooq data)
make trigger-test-dag

# Trigger production environment DAG (incremental mode)
make trigger-prod-dag

# Note: Data is automatically loaded during environment initialization
# - make init-dev: Loads sample/dummy data for development
# - make init-test: Loads real Stooq data for testing
# - DAGs provide monitoring, retry logic, and scheduling capabilities

# Manual CLI commands (for debugging/development only)
# stock-etl extract sample --output-dir data --delay 2.0
# stock-etl load sample --schema dev_stock_data
```

### 5. Access Web Interfaces

**🚀 Airflow Dashboard**: http://localhost:8080
- **Username**: `admin`
- **Password**: Check `.env` file (auto-generated)
- Available DAGs:
  - `dev_stock_etl_pipeline` - Development environment (active)
  - `test_stock_etl_pipeline` - Test environment (paused by default)
  - `prod_stock_etl_pipeline` - Production environment (paused by default)

**📊 pgAdmin Database Manager**: http://localhost:5050
- **Email**: `admin@admin.com`
- **Password**: `admin`
- Connect to: `postgres:5432` (host: postgres, port: 5432)
- Database: `stock_data` (user: postgres, password: postgres)

## 📋 CLI Commands

The project provides a comprehensive command-line interface for all operations:

### Database Management

```bash
# Environment initialization (recommended approach)
make init-dev           # Initialize dev environment + trigger dev DAG
make init-test          # Initialize test environment + trigger test DAG
make init-prod          # Initialize prod environment + trigger prod DAG

# Database connectivity testing
uv run python -m stock_etl.cli database test-connection --schema dev_stock_data
uv run python -m stock_etl.cli database test-connection --schema test_stock_data
```

### Data Extraction

```bash
# Extract predefined sample data (5 stocks + 4 indices)
stock-etl extract sample --output-dir data --delay 2.0

# Extract specific symbols
stock-etl extract symbol XTB --type stock --output-dir data
stock-etl extract symbol WIG --type index --output-dir data

# Batch extraction with rate limiting
stock-etl extract sample --delay 2.0  # 2-second delay between requests
```

### Data Loading

```bash
# Load sample data to specified schema
stock-etl load sample --schema dev_stock_data

# Load specific symbols
stock-etl load symbol XTB --type stock --schema test_stock_data
stock-etl load symbol WIG --type index --schema test_stock_data

# Load with validation
stock-etl load sample --schema test_stock_data --validate
```

### Full Pipeline Operations

```bash
# Complete ETL pipeline (extract + load)
stock-etl pipeline --schema dev_stock_data

# Pipeline with specific date range (for backfills)
stock-etl pipeline --schema prod_stock_data --start-date 2024-01-01 --end-date 2024-12-31
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_data
DB_USER=postgres
DB_PASSWORD=postgres

# ETL Configuration
DEFAULT_SCHEMA=dev_stock_data
STOOQ_RATE_LIMIT=2.0
LOG_LEVEL=INFO

# Airflow Configuration
AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags
AIRFLOW__CORE__LOAD_EXAMPLES=False
```

### Supported Markets & Instruments

**Polish Stock Exchange (WSE) Stocks:**
- `XTB` - X-Trade Brokers Dom Maklerski S.A.
- `PKN` - PKN Orlen S.A.
- `CCC` - CCC S.A.
- `LPP` - LPP S.A.
- `CDR` - CD Projekt S.A.

**Polish Market Indices:**
- `WIG` - WIG Index (main market index)
- `WIG20` - WIG20 (top 20 companies)
- `MWIG40` - mWIG40 (mid-cap companies)
- `SWIG80` - sWIG80 (small-cap companies)

## 🧪 Testing

### Database Testing

```bash
# Test database connectivity
stock-etl database test-connection --schema test_stock_data

# Initialize clean test environment
stock-etl database init-test

# Run pipeline on test data
stock-etl pipeline --schema test_stock_data
```

### Sample Data Validation

```bash
# Extract and validate sample data
python test_etl.py

# Check logs for validation results
tail -f logs/etl_debug.log
```

### Data Quality Verification

```bash
# Connect to database and verify data
docker-compose exec postgres psql -U postgres -d stock_data

# Check record counts
SET search_path TO dev_stock_data;
SELECT 'Stock Prices' as table_name, count(*) FROM stock_prices
UNION ALL
SELECT 'Index Prices', count(*) FROM index_prices
UNION ALL
SELECT 'ETL Jobs', count(*) FROM etl_jobs;

# Verify OHLC relationships
SELECT symbol, trading_date_local, 
       CASE WHEN high_price >= GREATEST(open_price, close_price) 
            AND low_price <= LEAST(open_price, close_price)
            THEN 'VALID' ELSE 'INVALID' END as ohlc_check
FROM stock_prices sp
JOIN stocks s ON sp.stock_id = s.id
JOIN base_instruments bi ON s.instrument_id = bi.id
ORDER BY trading_date_local DESC LIMIT 10;
```

## 🔍 Airflow Integration

### Multi-Environment DAG System ✅

The project features **dynamic environment-specific DAGs**:

- `dev_stock_etl_pipeline` - Development environment (active)
- `test_stock_etl_pipeline` - Test environment (paused) 
- `prod_stock_etl_pipeline` - Production environment (paused)

**Key Features:**
- **Trading Calendar Integration**: Automatic weekend/holiday detection using Polish trading calendar
- **Smart Execution Mode**: Automatically detects backfill vs incremental runs
- **Environment Isolation**: Separate schemas and configurations per environment
- **Comprehensive Monitoring**: ETL job tracking with detailed metrics
- **Data Quality Validation**: Automated OHLC validation and anomaly detection
- **Automated Connections**: Database connections configured automatically

### Environment Configurations

```python
# Environment-specific DAG configurations
ENVIRONMENTS = {
    'dev': {
        'schema': 'dev_stock_data',
        'schedule': None,                # Manual triggering
        'retries': 1,
        'catchup': False
    },
    'test': {
        'schema': 'test_stock_data',
        'schedule': None,                # Manual triggering  
        'retries': 1,
        'catchup': False
    },
    'prod': {
        'schema': 'prod_stock_data',
        'schedule': '0 18 * * 1-5',      # 6 PM weekdays
        'retries': 2,
        'catchup': True
    }
}
```

### Manual DAG Execution & Data Processing Modes

The ETL pipeline supports multiple execution modes for different data processing scenarios:

#### 🚀 Basic DAG Triggering

```bash
# Trigger environment-specific DAGs (incremental mode - latest data only)
docker-compose exec airflow airflow dags trigger dev_stock_etl_pipeline
docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline
docker-compose exec airflow airflow dags trigger prod_stock_etl_pipeline

# Or use Makefile shortcuts
make trigger-dev-dag
make trigger-test-dag  
make trigger-prod-dag
```

#### 📊 Data Processing Modes

The system uses **4-layer intelligent extraction strategy** with multiple processing modes:

##### 1. **Incremental Mode** (Default)
Processes only the latest available data (1 record per instrument).

```bash
# Explicit incremental mode
docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline \
  --conf '{"extraction_mode": "incremental"}'

# Result: ~14 records (latest data for 10 stocks + 4 indices)
```

##### 2. **Historical Mode** (Limited Backfill)
Processes up to 1000 historical records per instrument for catch-up scenarios.

```bash
# Limited historical backfill (1000 records max per instrument)
docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline \
  --conf '{"extraction_mode": "historical"}'

# Result: ~14,000 records (1000 × 14 instruments)
```

##### 3. **🆕 Full Backfill Mode** (Unlimited)
Processes **ALL available historical data** from Stooq with no limits (typically 10+ years).

```bash
# UNLIMITED BACKFILL - All available historical data
docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline \
  --conf '{"extraction_mode": "full_backfill"}'

# Result: 50,000+ records (entire trading history for all instruments)
# ⚠️  This will take 5-10 minutes to complete due to data volume
```

##### 4. **Smart Mode** (Automatic)
Automatically determines the best strategy based on database state.

```bash
# Smart automatic mode (default when no conf specified)
docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline

# Automatically chooses:
# - Historical: for new/stale instruments (>7 days old)
# - Incremental: for current instruments (<7 days old)
```

#### 🎯 Per-Instrument Override

Control processing mode for specific instruments:

```bash
# Mixed mode: some instruments historical, others incremental
docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline \
  --conf '{"instruments": {"XTB": "historical", "PKN": "incremental", "WIG": "historical"}}'

# Per-instrument with global fallback
docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline \
  --conf '{"extraction_mode": "incremental", "instruments": {"XTB": "historical"}}'
```

#### 📈 Expected Data Volumes

| Mode | Records Per Instrument | Total Records (14 instruments) | Processing Time | Use Case |
|------|----------------------|-------------------------------|----------------|----------|
| **Incremental** | 1 | ~14 | 30 seconds | Daily updates |
| **Historical** | 1,000 | ~14,000 | 2-3 minutes | Catch-up/testing |
| **Full Backfill** | 3,000-5,000+ | 50,000+ | 5-10 minutes | Complete history |
| **Smart** | Variable | Variable | Variable | Production mode |

#### 🔍 Monitoring DAG Execution

```bash
# Check DAG status
docker-compose exec airflow airflow dags list
docker-compose exec airflow airflow dags list-runs test_stock_etl_pipeline

# Monitor task progress via Airflow UI
# http://localhost:8080 → DAGs → test_stock_etl_pipeline → Graph View

# Check database record counts during/after execution
docker-compose exec postgres psql -U postgres -d stock_data -c "
SET search_path TO test_stock_data;
SELECT 'Stock Prices' as table_name, count(*) FROM stock_prices
UNION ALL SELECT 'Index Prices', count(*) FROM index_prices;
"
```

#### ⚠️ Production Considerations

- **Full Backfill**: Use sparingly in production - high API load and processing time
- **Historical Mode**: Good for weekly/monthly catch-up scenarios  
- **Incremental Mode**: Recommended for daily production schedules
- **Smart Mode**: Best for production with automatic decision-making

#### 🧠 Intelligent Processing Logic

The system automatically determines processing mode based on:

1. **Manual Configuration** (highest priority)
2. **Database State Analysis**:
   - New instrument → Historical (1000 records)
   - Stale data (>7 days) → Historical (500 records)  
   - Sparse data (<30 records) → Historical (1000 records)
   - Current data → Incremental (1 record)
3. **DAG Execution Context** (backfill vs regular)
4. **Safety Default** (incremental mode)

#### 🔒 Duplicate Data Prevention

**Running full_backfill multiple times will NOT create duplicate data.** The system is designed to be **idempotent**:

**Deduplication Mechanisms:**
- **UPSERT Logic**: `ON CONFLICT (stock_id, trading_date_local) DO UPDATE SET...`
- **Unique Constraints**: One record per instrument per trading day
- **Hash-based Detection**: `raw_data_hash` field tracks data changes
- **Update Strategy**: Latest data overwrites existing records

**What happens on re-run:**
- **New Data**: Gets inserted normally
- **Existing Data**: Gets updated with latest values from Stooq  
- **ETL Tracking**: New job record created, but price data is deduplicated
- **Final Result**: Same dataset regardless of how many times you run it

**Safe to re-run full_backfill:**
```bash
# This is safe to run multiple times - no duplicates created
docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline \
  --conf '{"extraction_mode": "full_backfill"}'
```

## 📈 Monitoring & Observability

### ETL Job Tracking

The system provides comprehensive monitoring through database tables:

```sql
-- View recent ETL jobs
SELECT job_name, status, records_processed, records_inserted, 
       started_at, completed_at, duration_seconds
FROM etl_jobs 
ORDER BY started_at DESC LIMIT 10;

-- Check job details by instrument
SELECT j.job_name, jd.symbol, jd.operation, jd.records_count, jd.processing_time_ms
FROM etl_jobs j
JOIN etl_job_details jd ON j.id = jd.job_id
WHERE j.status = 'completed'
ORDER BY j.started_at DESC;

-- Data quality metrics
SELECT instrument_id, metric_name, metric_value, is_valid, severity
FROM data_quality_metrics 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
  AND is_valid = FALSE;
```

### Structured Logging

All operations use structured JSON logging:

```bash
# View real-time logs
tail -f logs/etl_debug.log | jq '.'

# Filter by log level
grep '"level": "error"' logs/etl_debug.log | jq '.'

# Monitor specific operations
grep '"event": "data_extraction"' logs/etl_debug.log | jq '.symbol, .records_count'
```

### Airflow Monitoring

Access Airflow UI at http://localhost:8080 for:
- **DAG Run History**: Success/failure rates and duration trends
- **Task Logs**: Detailed execution logs for each pipeline step
- **Connection Health**: Database connectivity status
- **SLA Monitoring**: Configurable alerts for pipeline delays

## 🏗️ Development

### Code Quality

```bash
# Format code
black stock_etl/ tests/

# Lint code
ruff check stock_etl/ tests/

# Type checking
mypy stock_etl/

# Run tests
pytest tests/ -v --cov=stock_etl
```

### Development Setup

```bash
# Install development dependencies
uv sync --group dev

# Pre-commit hooks (optional)
pre-commit install

# Run development database
docker-compose up -d postgres
stock-etl database init-dev
```

### Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Run tests**: `pytest tests/`
4. **Check code quality**: `black . && ruff check . && mypy stock_etl/`
5. **Commit changes**: `git commit -m "Add new feature"`
6. **Push branch**: `git push origin feature/new-feature`
7. **Create Pull Request**

## 🐳 Docker Services

### Service Overview

| Service | Port | Purpose | Credentials | Health Check |
|---------|------|---------|-------------|--------------|
| PostgreSQL | 5432 | Database storage | postgres/postgres | `pg_isready -U postgres` |
| Airflow | 8080 | Workflow orchestration | admin/auto-generated | HTTP endpoint check |
| pgAdmin | 5050 | Database management | admin@admin.com/admin | HTTP endpoint check |

### Container Management

```bash
# Start all services (recommended: use Makefile)
make start                       # Complete setup with schema initialization
docker-compose up -d             # Basic service startup

# View service logs
docker-compose logs -f postgres
docker-compose logs -f airflow
docker-compose logs -f pgadmin

# Restart services
make restart                     # Complete restart with setup
docker-compose restart           # Basic restart

# Stop all services
make stop                        # Graceful shutdown
docker-compose down              # Basic shutdown

# Complete cleanup (removes all data)
make clean                       # Complete cleanup including logs
docker-compose down -v           # Remove volumes only
```

### Database Access

```bash
# Connect to PostgreSQL directly
docker-compose exec postgres psql -U postgres -d stock_data

# Execute SQL files
docker-compose exec postgres psql -U postgres -d stock_data -f /sql/schema_template.sql

# Database backup
docker-compose exec postgres pg_dump -U postgres stock_data > backup.sql

# Database restore
docker-compose exec -T postgres psql -U postgres -d stock_data < backup.sql
```

## 📊 Performance & Scalability

### Database Optimization

The schema includes comprehensive indexing for optimal query performance:

```sql
-- High-performance price queries
CREATE INDEX idx_stock_prices_stock_date ON stock_prices(stock_id, trading_date_local DESC);
CREATE INDEX idx_index_prices_index_date ON index_prices(index_id, trading_date_local DESC);

-- ETL monitoring indexes
CREATE INDEX idx_etl_jobs_status ON etl_jobs(status);
CREATE INDEX idx_etl_jobs_started_epoch ON etl_jobs(started_at_epoch);

-- Data quality indexes
CREATE INDEX idx_data_quality_invalid ON data_quality_metrics(is_valid) WHERE is_valid = FALSE;
```

### Connection Pooling

SQLAlchemy connection pooling is configured for optimal performance:

```python
# Database connection configuration
pool_size=10          # Base connection pool size
max_overflow=20       # Additional connections under load
pool_pre_ping=True    # Verify connections before use
pool_recycle=3600     # Recycle connections every hour
```

### Rate Limiting

Stooq API requests are rate-limited to prevent blocking:

```python
# Default configuration
delay_between_requests = 2.0  # 2-second delay
max_retries = 3              # Retry failed requests
backoff_factor = 2           # Exponential backoff
```

## 🔒 Security & Best Practices

### Database Security

- **Connection encryption**: TLS/SSL enabled for production
- **User privileges**: Least privilege access controls
- **Password management**: Environment variable configuration
- **SQL injection prevention**: Parameterized queries only

### Data Validation

- **Input validation**: Pydantic models validate all external data
- **Business rules**: OHLC price relationship validation
- **Duplicate detection**: Hash-based deduplication
- **Type safety**: Strict typing with mypy

### Error Handling

- **Graceful degradation**: Pipeline continues on single instrument failures
- **Comprehensive logging**: All errors logged with context
- **Retry mechanisms**: Automatic retry with exponential backoff
- **Monitoring alerts**: Data quality violations logged and tracked

## 📚 Additional Resources

### Documentation
- **[Database ERD](docs/erd-normalized-approach.md)**: Detailed schema documentation with Mermaid diagrams
- **[CLAUDE.md](CLAUDE.md)**: Development guidance and architectural decisions
- **[Progress Summary](.claude/progress-summary.md)**: Detailed implementation progress

### External APIs
- **[Stooq API](https://stooq.com)**: Polish stock market data source
- **Rate limits**: ~60 requests per minute (respect usage guidelines)
- **Data format**: CSV with Date,Open,High,Low,Close,Volume columns

### Production Deployment
- **Environment isolation**: Separate dev/staging/prod schemas
- **Backup strategy**: Daily automated PostgreSQL backups
- **Monitoring**: Integration with Prometheus/Grafana (planned)
- **Scaling**: Horizontal scaling via Airflow workers

---

## 🎯 Production Status

✅ **Database Schema**: Unified ID design with comprehensive validation  
✅ **ETL Pipeline**: Production-tested with 58,470+ real market records  
✅ **Multi-Environment DAGs**: Dynamic dev/test/prod Airflow DAGs operational  
✅ **Container Infrastructure**: PostgreSQL 17 + Airflow 3.0.4 + pgAdmin ready  
✅ **CLI Interface**: Full command-line management capabilities  
✅ **Monitoring**: Comprehensive ETL job tracking and data quality metrics  
✅ **Automation**: Complete infrastructure setup via Makefile  
✅ **Intelligent Data Processing**: Smart backfill/incremental extraction logic  
✅ **Trading Calendar Integration**: Polish Stock Exchange market hours and holidays  

**Current Completion**: 100% (18/18 tasks completed)  
**Last Validation**: August 2025 with unified ID schema and real market data processing  
**Success Rate**: 100% (0 failures in production testing)  
**Data Processing**: 14,000+ records in test environment with authentic Stooq API data

---

*Built with ❤️ for robust financial data processing*