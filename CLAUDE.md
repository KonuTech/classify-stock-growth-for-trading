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

### Complete Infrastructure Deployment
```bash
# 🚀 COMPLETE DEPLOYMENT: services + schemas + DAGs (recommended)
make start

# Alternative: Initialize specific environment
make init-dev    # Initialize dev environment + trigger dev DAG
make init-test   # Initialize test environment + trigger test DAG
make init-prod   # Initialize prod environment + trigger prod DAG

# Manual development setup
uv sync --group dev
docker-compose up -d postgres pgadmin airflow
```

### Individual Environment Setup
```bash
# Install dependencies (includes ML libraries: scikit-learn, TA-Lib, imbalanced-learn)
uv sync

# Install with development dependencies (includes jupyterlab, plotting libraries)
uv sync --group dev

# Initialize specific database schemas
uv run python -m stock_etl.cli database init-dev
uv run python -m stock_etl.cli database init-test

# Test database connectivity
uv run python -m stock_etl.cli database test-connection --schema dev_stock_data

# Verify ML dependencies (TA-Lib requires system installation)
uv run python -c "import talib; print('TA-Lib version:', talib.__version__)"
```

### ML Dependencies & System Requirements
```bash
# TA-Lib system installation (required for technical indicators)
# Ubuntu/Debian:
sudo apt-get install libta-lib-dev

# macOS:
brew install ta-lib

# Windows (via conda):
conda install -c conda-forge ta-lib

# Verify all ML dependencies
uv run python -c "
import pandas, numpy, sklearn, talib, imblearn
print('✅ All ML dependencies installed successfully')
print(f'pandas: {pandas.__version__}')
print(f'scikit-learn: {sklearn.__version__}')
print(f'TA-Lib: {talib.__version__}')
"
```

### ETL Operations
```bash
# Extract sample Polish market data
uv run python -m stock_etl.cli extract sample --output-dir data --delay 2.0

# Extract single symbol
uv run python -m stock_etl.cli extract symbol XTB --type stock --output-dir data

# Load sample data into database
uv run python -m stock_etl.cli load sample --schema dev_stock_data

# Load single symbol
uv run python -m stock_etl.cli load symbol XTB --type stock --schema dev_stock_data

# Run complete ETL pipeline
uv run python -m stock_etl.cli pipeline --schema dev_stock_data
```

### Makefile Automation Commands
```bash
# Infrastructure management
make help                    # Show all available commands
make start                   # Complete deployment (recommended)
make stop                    # Stop all services
make restart                 # Restart with complete setup
make clean                   # Stop and remove all data/logs

# Environment management
make trigger-dev-dag         # Trigger development ETL DAG
make trigger-test-dag        # Trigger test ETL DAG
make trigger-prod-dag        # Trigger production ETL DAG
make setup-airflow           # Setup Airflow connections only
make fix-schema-permissions  # Fix database permissions
make extract-credentials     # Extract service credentials to .env
```

### Code Quality
```bash
# Format code
uv run black stock_etl/ stock_ml/ tests/

# Lint code
uv run ruff check stock_etl/ stock_ml/ tests/

# Type checking
uv run mypy stock_etl/

# Run ETL pipeline tests
uv run python test_etl.py

# Run ML pipeline tests (comprehensive)
uv run python stock_ml/test_pipeline.py 1    # Complete ML pipeline test
uv run python stock_ml/test_pipeline.py 2    # Data pipeline only
uv run python stock_ml/test_pipeline.py 3    # Multi-stock test

# Run tests with pytest (if tests/ directory is populated)
uv run pytest tests/ -v --cov=stock_etl
```

### Interactive Development
```bash
# Launch JupyterLab for interactive analysis
uv run --with jupyter jupyter lab

# Start JupyterLab with specific notebook
uv run jupyter lab docs/stock_analysis_reports_fixed.ipynb

# Access Jupyter interface
# URL: http://localhost:8888 (token will be displayed in terminal)
```

## Database Schemas

### Schema Structure
**Core ETL Tables:**
- **exchanges**: WSE, NewConnect, etc.
- **base_instruments**: Common instrument data (symbol, name, type)
- **stocks**: Stock-specific data (company_name, sector)
- **indices**: Index-specific data (methodology, base_value)
- **stock_prices**: Daily OHLCV data for stocks
- **index_prices**: Daily OHLCV data for indices
- **etl_jobs**: Job tracking and monitoring
- **data_quality_metrics**: Automated data validation results

**ML Pipeline Tables:**
- **ml_models**: Model metadata, hyperparameters, and performance metrics
- **ml_feature_data**: Engineered features with technical indicators and target variables
- **ml_predictions**: Model predictions with probabilities and confidence scores
- **ml_backtest_results**: Trading strategy performance and risk metrics

### Schema Initialization Files
- `sql/schema_template.sql.j2`: Unified Jinja2 template for all environments
- `sql/dev_dummy_data.sql`: Sample data for development
- `sql/init-databases.sql`: Multi-database initialization script

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
- **PostgreSQL 17**: Available on port 5432 (postgres/postgres)
- **Airflow 3.0.4**: Available on port 8080 (admin/auto-generated-password)
- **pgAdmin**: Available on port 5050 (admin@admin.com/admin)
- **Airflow Metadata DB**: localhost:5432/airflow_metadata (airflow/airflow)
- **Stock Business DB**: localhost:5432/stock_data (stock/stock)

### Docker Management
```bash
# View service logs
docker-compose logs -f postgres
docker-compose logs -f airflow
docker-compose logs -f pgadmin

# Restart services (automated)
make restart

# Manual restart
docker-compose restart

# Complete infrastructure reset
make clean
```

## Airflow Integration

### Multi-Environment DAG Architecture ✅ WORKING
Dynamic environment-specific DAGs in `stock_etl/airflow_dags/stock_etl_dag.py`:

- **Environment-Specific DAGs**: `dev_stock_etl_pipeline` (active), `test_stock_etl_pipeline` (paused), `prod_stock_etl_pipeline` (paused)
- **Smart Execution Mode Detection**: Automatically detects backfill vs incremental runs
- **Polish Trading Calendar Integration**: Uses `polish_trading_calendar.py` for market day validation
- **Comprehensive ETL Job Tracking**: Full lifecycle tracking with Airflow context
- **Data Quality Validation**: Automated OHLC validation and anomaly detection
- **Error Handling and Retry Logic**: Graceful failure handling with detailed logging
- **Automated Connections**: postgres_default and postgres_stock connections configured via docker-compose

### ML Pipeline DAG Architecture ✅ WORKING
Dynamic ML training DAGs in `stock_etl/airflow_dags/stock_ml_dag.py`:

- **Per-Stock ML DAGs**: Dynamically generated DAGs for each stock symbol in test_stock_data
- **7-Day Growth Prediction**: Binary classification for weekly stock growth forecasting
- **Complete ML Pipeline**: Data extraction → feature engineering → model training → backtesting → database storage
- **Schema Validation**: Comprehensive data validation against ML table schemas before insertion
- **XGBoost Classification**: GPU-accelerated gradient boosting with hyperparameter optimization
- **Production Schedule**: Daily execution at 6 PM (after market close, Monday-Friday)
- **Database Integration**: All ML artifacts stored in test_stock_data schema for web application access

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

### DAG Task Flow
1. **check_prerequisites** - Validates trading calendar and execution context
2. **create_etl_job** - Creates ETL job record with comprehensive metadata
3. **extract_and_transform** - Data extraction with source tracking
4. **load_data** - Database loading with detailed per-instrument tracking
5. **validate_data_quality** - Automated quality checks (OHLC, gaps, volumes)
6. **finalize_etl_session** - Job completion with final status and metrics

### Manual DAG Operations
```bash
# Trigger environment-specific DAGs
make trigger-dev-dag     # Recommended: via Makefile
make trigger-test-dag
make trigger-prod-dag

# Direct Airflow CLI commands
docker-compose exec airflow airflow dags trigger dev_stock_etl_pipeline
docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline
docker-compose exec airflow airflow dags trigger prod_stock_etl_pipeline

# List DAG runs
docker-compose exec airflow airflow dags list-runs dev_stock_etl_pipeline

# Check DAG status
docker-compose exec airflow airflow dags show dev_stock_etl_pipeline

# Monitor task logs
docker-compose exec airflow airflow tasks logs dev_stock_etl_pipeline extract_and_transform 2025-08-18

# Clear DAG run for retry
docker-compose exec airflow airflow dags clear dev_stock_etl_pipeline

# ML DAG Operations (dynamic per-stock DAGs)
docker-compose exec airflow airflow dags list | grep ml_training   # List all ML DAGs
docker-compose exec airflow airflow dags trigger ml_training_xtb   # Trigger specific stock ML training
docker-compose exec airflow airflow tasks logs ml_training_xtb ml_training_task 2025-08-20   # Monitor ML task logs
```

### Current Operational Status (August 2025)
**✅ VALIDATION COMPLETE**: Dynamic multi-environment DAG system operational

**Recent Test Results:**
- Development DAG: ✅ Successfully executed (latest run: success)
- Database Connections: ✅ postgres_default and postgres_stock working
- Schema Permissions: ✅ dev_stock_data and test_stock_data accessible
- Trading Calendar Integration: ✅ Polish market calendar validation active
- ETL Job Tracking: ✅ Comprehensive metadata and lifecycle tracking

**DAG Status:**
- `dev_stock_etl_pipeline`: Active (is_paused = False)
- `test_stock_etl_pipeline`: Paused (is_paused = True)
- `prod_stock_etl_pipeline`: Paused (is_paused = True)

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
- **ETL Pipeline**: Uses `structlog` with JSON output, logs written to `logs/etl_debug.log`
- **ML Pipeline**: Centralized logging via `stock_ml.logging_config` module
- **Context-Independent**: All logs saved to project root `./logs/` regardless of execution directory
- Different log levels for development vs production

### ML Pipeline Logging
- **Centralized Configuration**: `stock_ml.logging_config.get_ml_logger()` for consistent setup
- **Individual Log Files**: Each ML module gets dedicated log file in `logs/stock_ml/`
- **Dual Output**: Both file and console logging with timestamps
- **Project Root Resolution**: Uses `CLAUDE.md` marker file to find project root directory
- **Execution Context Agnostic**: Works from notebooks, project root, or any subdirectory

```python
# Usage in ML modules
from .logging_config import get_ml_logger
logger = get_ml_logger(__name__)  # Creates logs/stock_ml/{module_name}.log
```

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

## Machine Learning Pipeline (`stock_ml/`)

### ML Architecture Components
- **stock_ml.data_extractor**: Multi-stock data extraction from PostgreSQL with quality filtering
- **stock_ml.feature_engineering**: TA-Lib technical indicators and market features
- **stock_ml.preprocessing**: Data preprocessing with feature selection (no SMOTE - inappropriate for time series)
- **stock_ml.model_trainer_optimized**: GPU-accelerated XGBoost classification with grid search optimization
- **stock_ml.backtesting**: Trading strategy backtesting with performance metrics
- **stock_ml.database_operations**: Complete ML data persistence layer with CRUD operations for all ML tables
- **stock_ml.schema_validator**: Data validation against database schema before insertion
- **stock_ml.test_pipeline**: Comprehensive testing framework for ML pipeline validation
- **stock_ml.logging_config**: Centralized logging utility for consistent ML module logging

### ML Pipeline Flow
1. **Data Extraction**: Multi-stock data from `test_stock_data` schema with quality filtering
2. **Feature Engineering**: Technical indicators (RSI, MACD, Bollinger Bands, etc.) using TA-Lib
3. **Target Generation**: Binary classification for stock growth prediction (30-day forward returns)
4. **Data Preprocessing**: Missing value handling, feature selection, no synthetic balancing
5. **Model Training**: XGBoost with `scale_pos_weight` parameter for imbalanced data
6. **Backtesting**: Trading strategy evaluation with risk-adjusted performance metrics

### Essential ML Commands

```bash
# Complete ML pipeline test (recommended)
uv run python stock_ml/test_pipeline.py 1

# Test modes available:
# 1. Single stock ML test (XTB) - Complete pipeline with training
# 2. Single stock data test (XTB) - Data pipeline only  
# 3. Multi-stock data test - All stocks data pipeline
# 4. Interactive mode - Choose symbol and configuration

# Direct module execution
uv run python -m stock_ml.test_pipeline 1

# Example single stock training
uv run python -c "
from stock_ml.test_pipeline import test_single_stock_pipeline
test_single_stock_pipeline('XTB', include_ml=True)
"
```

### ML Configuration & Features

**Target Variable**: Binary classification for 30-day forward stock growth
- Positive class: Stock growth > threshold
- Uses chronological train/validation/test splits (no data leakage)
- Class imbalance handled via `class_weight='balanced'` in Random Forest

**Feature Engineering Pipeline**:
- **Price Features**: Returns, log returns, volatility measures
- **Technical Indicators**: RSI, MACD, Bollinger Bands, momentum oscillators
- **Moving Averages**: Multiple timeframes (5, 10, 20, 50, 200 days)
- **Volume Features**: Volume ratios, volume moving averages
- **Market Structure**: Support/resistance levels, trend indicators

**Model Architecture**:
- **Algorithm**: XGBoost Classifier (GPU-accelerated gradient boosting with native NaN handling)
- **Feature Selection**: Top 25-50 features selected by XGBoost importance
- **Hyperparameter Tuning**: Grid search with cross-validation
- **Validation Strategy**: Time-series aware train/validation/test splits

### ML Pipeline Testing & Validation

**Test Execution Results**:
```bash
# Expected output structure for successful test
🧪 Stock ML Pipeline Tests
==============================================
🚀 Running Single Stock ML Test (XTB)...

📊 STEP 1: DATA EXTRACTION FOR XTB
✅ Extracted 1337 records for XTB
   Date range: 2019-05-23 to 2025-08-19

🔧 STEP 2: FEATURE ENGINEERING FOR XTB  
✅ Engineered 87 features for XTB
   Target distribution: Positive 46.2%, Negative 53.8%

📈 STEP 3: DATA SPLITTING FOR XTB
✅ Train: 802, Val: 267, Test: 268

🔄 STEP 4: PREPROCESSING FOR XTB
✅ Preprocessing completed for XTB
   Features: 86 → 25
   Class imbalance ratio: 1.2:1
   
🤖 STEP 5: MODEL TRAINING FOR XTB
✅ Model training completed for XTB
   Best CV score: 0.5691
   Validation ROC-AUC: 0.5734
   
📋 STEP 6: TEST EVALUATION FOR XTB
✅ Test evaluation completed for XTB
   Test ROC-AUC: 0.5612
   Test Accuracy: 0.5560
   Test F1-Score: 0.5455

💰 STEP 7: BACKTESTING FOR XTB
✅ Backtesting completed for XTB
   Total return: 12.34%
   Win rate: 52.17%
   Total trades: 46
   Sharpe ratio: 0.445

🎯 FINAL ASSESSMENT FOR XTB
   Model Quality: ✅ GOOD
   Trading Quality: ✅ GOOD  
   Overall: ✅ SUCCESS
```

### ML Quality Thresholds

**Model Performance Criteria**:
- **Minimum ROC-AUC**: 0.55 (better than random)
- **Minimum Accuracy**: 0.52 (accounting for class imbalance)
- **Minimum Win Rate**: 40% (backtesting performance)

**Feature Engineering Quality**:
- **Minimum Records**: 500 trading days per stock
- **Minimum Years**: 2.0 years of data
- **Feature Count**: 25-50 selected features (from 80+ engineered)
- **Missing Values**: < 5% after preprocessing

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

### ML Pipeline Design Patterns
- **Time Series Awareness**: Chronological splits prevent data leakage
- **Feature Engineering**: TA-Lib integration for reliable technical indicators
- **Class Imbalance**: Uses `scale_pos_weight` parameter in XGBoost instead of SMOTE (inappropriate for time series)
- **Model Selection**: XGBoost chosen for superior performance on tabular data and native missing value handling
- **Backtesting Framework**: Walk-forward analysis with realistic trading costs

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

## Infrastructure & Operations Assessment (August 2025)

### Project Status Analysis
**Current State**: Complete ETL pipeline with integrated ML capabilities (100% complete, 19/19 tasks)

**Key Achievements:**
- ✅ Complete PostgreSQL 17 + Airflow 3.0.4 containerized infrastructure
- ✅ Database separation architecture (airflow_metadata vs stock_data databases)
- ✅ Unified Jinja2 schema template system for multi-environment deployment
- ✅ Production validation with 58,470+ real market records (100% success rate)
- ✅ Dynamic multi-environment Airflow DAGs with trading calendar integration
- ✅ Automated credential management and service orchestration via Makefile
- ✅ **NEW**: Dynamic DAG system operational with successful dev environment execution
- ✅ **NEW**: Complete ML pipeline with TA-Lib technical indicators and GPU-accelerated XGBoost classification
- ✅ **NEW**: Comprehensive backtesting framework with risk-adjusted performance metrics

### Project Enhancement Opportunities
All core functionality is complete. Future enhancements could include:

1. **Advanced ML Models**: LSTM/GRU for time series, ensemble methods, feature selection optimization
2. **Real-time Processing**: Streaming data pipeline for intraday trading signals
3. **Portfolio Optimization**: Multi-asset allocation strategies and risk management
4. **Advanced Backtesting**: Transaction costs, slippage modeling, walk-forward analysis
5. **Production Monitoring**: Health check endpoints, alerting framework, performance dashboards
6. **Additional Markets**: Integration with other exchanges and data providers

### Current Monitoring Capabilities
**Already Implemented:**
- ETL job lifecycle tracking in `etl_jobs` table with detailed metrics
- Data quality validation pipeline with `data_quality_metrics` storage
- Comprehensive structured logging via `structlog` with JSON output
- Airflow DAG monitoring with task-level success/failure tracking
- Database constraint validation and OHLC price relationship checks

**Production Monitoring Queries Available:**
```sql
-- ETL job performance monitoring
SELECT job_name, status, records_processed, duration_seconds, started_at 
FROM etl_jobs 
ORDER BY started_at DESC LIMIT 10;

-- Data quality issue detection
SELECT instrument_id, metric_name, is_valid, severity 
FROM data_quality_metrics 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days' 
  AND is_valid = FALSE;

-- Pipeline health check
SELECT 
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_jobs,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
    ROUND(AVG(duration_seconds), 2) as avg_duration_seconds
FROM etl_jobs 
WHERE started_at >= CURRENT_DATE - INTERVAL '30 days';

-- ML model performance monitoring
SELECT 
    m.model_version,
    bi.symbol,
    m.test_roc_auc,
    m.test_accuracy,
    br.total_return,
    br.sharpe_ratio,
    br.win_rate,
    m.created_at
FROM ml_models m
JOIN base_instruments bi ON m.instrument_id = bi.id
LEFT JOIN ml_backtest_results br ON m.id = br.model_id
ORDER BY m.created_at DESC LIMIT 10;

-- ML feature data quality check
SELECT 
    COUNT(*) as total_features,
    COUNT(CASE WHEN feature_completeness > 0.95 THEN 1 END) as high_quality_features,
    ROUND(AVG(feature_completeness), 3) as avg_completeness,
    ROUND(AVG(data_quality_score), 3) as avg_quality_score
FROM ml_feature_data 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';
```

### Infrastructure Readiness Assessment
**Production Capabilities:**
- **Database Architecture**: Expert A's separation approach provides optimal scalability
- **Container Orchestration**: Full Docker Compose stack with health checks
- **Schema Management**: Template-based deployment supports dev/test/prod environments  
- **Data Processing**: Validated pipeline handles thousands of records reliably
- **Calendar Integration**: WSE trading calendar prevents weekend/holiday execution
- **Error Recovery**: Comprehensive retry logic and graceful failure handling

**Deployment Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Airflow UI    │    │  ETL Pipeline   │    │  PostgreSQL 17  │
│   (Port 8080)   │    │   (Python)      │    │   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    pgAdmin      │    │   Docker        │    │  Automated      │
│   (Port 5050)   │    │   Compose       │    │  Credentials    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technical Foundation Strengths
1. **Normalized Database Design**: Properly designed 3NF/BCNF schema supports complex financial data
2. **Type Safety**: Pydantic models provide runtime validation and IDE support  
3. **Performance Optimization**: Strategic indexing and connection pooling for scalability
4. **Data Integrity**: Multi-layer validation prevents corrupt data entry
5. **Extensibility**: Clean architecture allows easy addition of new markets/instruments
6. **Maintainability**: Comprehensive logging and error tracking for debugging

### ML Pipeline Capabilities (Newly Implemented)
**Feature Engineering**:
- 80+ technical indicators via TA-Lib integration
- Multi-timeframe moving averages and volatility measures
- Price momentum and mean reversion signals
- Volume-based indicators and market microstructure features

**Model Training & Evaluation**:
- XGBoost classification with GPU acceleration and hyperparameter tuning
- Time-series aware train/validation/test splits
- Feature selection via XGBoost native importance scoring
- Class imbalance handling with `scale_pos_weight` parameter

**Backtesting & Performance**:
- Trading strategy simulation with realistic transaction costs
- Risk-adjusted performance metrics (Sharpe ratio, win rate, drawdown)
- Walk-forward analysis for temporal validation
- Comprehensive performance reporting and visualization

**Testing & Validation**:
- Comprehensive test suite in `stock_ml/test_pipeline.py`
- Multi-stock testing capabilities
- Interactive mode for custom stock analysis
- Quality thresholds and automated assessment