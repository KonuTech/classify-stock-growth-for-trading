# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive AI-powered stock analysis platform that combines ETL data processing, GPU-accelerated machine learning, and an interactive web application. The project extracts financial data from Stooq (Polish Stock Exchange), stores it in a normalized PostgreSQL database, provides Apache Airflow orchestration, trains XGBoost models for stock growth prediction, and serves real-time analysis through a React web dashboard.

## Core Architecture

### Database Design
- **Normalized schema** with separate tables for exchanges, instruments, stocks, indices, and price data
- **Multi-schema support**: `dev_stock_data`, `test_stock_data`, `prod_stock_data`
- **Timezone-aware**: Stores both local and UTC timestamps with epoch support
- **Data integrity**: Comprehensive constraints and validation at database level
- **ML tables**: Complete ML pipeline storage (models, features, predictions, backtests)

### Key Components
**ETL Pipeline:**
- **stock_etl.core.models**: Pydantic models for validation and type safety
- **stock_etl.core.database**: Database connection management with pooling
- **stock_etl.data.stooq_extractor**: Data extraction from Stooq financial service
- **stock_etl.database.operations**: Database CRUD operations for normalized schema
- **stock_etl.cli**: Command-line interface for all ETL operations
- **stock_etl.airflow_dags.stock_etl_dag**: Unified Airflow DAG with smart execution mode detection
- **stock_etl.utils.dag_utils**: 4-layer intelligent processing logic for execution mode detection
- **stock_etl.utils.polish_trading_calendar**: Warsaw Stock Exchange trading calendar

**ML Pipeline:**
- **stock_ml.data_extractor**: Multi-stock data extraction from PostgreSQL with quality filtering
- **stock_ml.feature_engineering**: 180+ TA-Lib technical indicators and physics-inspired features
- **stock_ml.model_trainer_optimized**: GPU-accelerated XGBoost classification with grid search
- **stock_ml.backtesting**: Trading strategy backtesting with performance metrics
- **stock_ml.database_operations**: Complete ML data persistence layer with CRUD operations
- **stock_ml.schema_validator**: Data validation against database schema before insertion

**Web Application:**
- **web-app/backend/src/index.js**: Express.js API server with PostgreSQL integration
- **web-app/frontend/src/App.tsx**: React dashboard with TypeScript and Tailwind CSS
- **web-app/frontend/src/components/**: Reusable UI components (StockDetail, StockFilter, charts)
- **web-app/frontend/src/hooks/**: Custom React hooks for data fetching and state management

### Data Flow
1. **ETL Pipeline**: Extract data from Stooq API → Validate using Pydantic models → Load into PostgreSQL → Track jobs
2. **ML Pipeline**: Extract from PostgreSQL → Feature engineering (180+ features) → XGBoost training → Backtesting → Store results  
3. **Web Application**: React frontend ↔ Express.js API ↔ PostgreSQL (`prod_stock_data` schema)

## Essential Commands

### Complete Infrastructure Deployment
```bash
# 🚀 COMPLETE DEPLOYMENT: services + schemas + DAGs + automatic data loading (recommended)
make start

# 🌐 COMPLETE PLATFORM: includes web application (React frontend + Express.js backend)
make start-with-web

# 🏗️ INFRASTRUCTURE ONLY: services without automatic DAG triggering
make start-infrastructure

# Alternative: Initialize specific environment
make init-dev    # Initialize dev environment + trigger dev DAG (smart detection)
make init-test   # Initialize test environment + trigger test DAG (full_backfill - 50,000+ records)
make init-prod   # Initialize prod environment + trigger prod DAG (full_backfill + ML tables)

# Manual development setup
uv sync --group dev
docker-compose up -d postgres pgadmin airflow
```

### Individual Environment Setup
```bash
# Install dependencies (includes ML libraries: scikit-learn, TA-Lib, XGBoost, imbalanced-learn)
uv sync

# Install with development dependencies (includes jupyterlab, plotting libraries)
uv sync --group dev

# Initialize specific database schemas  
uv run python -m stock_etl.cli database init-dev
uv run python -m stock_etl.cli database init-test
uv run python -m stock_etl.cli database init-prod  # Includes ML tables

# Test database connectivity
uv run python -m stock_etl.cli database test-connection --schema dev_stock_data

# Verify ML dependencies (TA-Lib requires system installation)
uv run python -c "import talib, xgboost; print('TA-Lib version:', talib.__version__); print('XGBoost version:', xgboost.__version__)"
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
import pandas, numpy, sklearn, talib, imblearn, xgboost
print('✅ All ML dependencies installed successfully')
print(f'pandas: {pandas.__version__}')
print(f'scikit-learn: {sklearn.__version__}')
print(f'TA-Lib: {talib.__version__}')
print(f'XGBoost: {xgboost.__version__}')
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
make start                   # Complete deployment with automatic DAG triggering (recommended)
make stop                    # Stop all services
make restart                 # Restart infrastructure only (Docker services)
make docker-restart          # Restart ALL Docker services (preserves data)
make docker-clean            # CLEAN restart with database reinitialization (deletes data)
make clean                   # Stop and remove all data/logs

# Environment management
make trigger-dev-dag         # Trigger development ETL DAG (smart detection)
make trigger-test-dag        # Trigger test ETL DAG (explicit full_backfill - 50,000+ records)
make trigger-prod-dag        # Trigger production ETL DAG (explicit full_backfill - 50,000+ records)
make setup-airflow           # Setup Airflow connections only
make fix-schema-permissions  # Fix database permissions
make extract-credentials     # Extract service credentials to .env

# ML DAGs (Test & Production Only)
make trigger-test-ml-dags    # Trigger all test ML DAGs (test_ml_pipeline_*)
make trigger-prod-ml-dags    # Trigger all production ML DAGs (prod_ml_pipeline_*)

# Web Application (Docker Production)
make start-with-web          # Start complete infrastructure WITH Docker web application
make web-start               # Start Docker web application services only
make web-stop                # Stop Docker web application services
make web-restart             # Restart Docker web application with latest changes
make web-build               # Build web application Docker images
make web-status              # Show web application status and URLs

# Web Application (Development - Local)
make dev-restart             # Restart EVERYTHING (infrastructure + development web app)
make dev-web-install         # Install frontend dependencies  
make dev-web-start           # Start backend and frontend in development mode
make dev-web-backend         # Start only backend API server
make dev-web-frontend        # Start only frontend development server
make dev-web-restart         # Restart development web services only
make dev-web-stop            # Stop development web services
make dev-web-status          # Show development web services status
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
uv run jupyter lab docs/notebooks/XGBoost_Pipeline_Validation-05.ipynb

# Access Jupyter interface
# URL: http://localhost:8888 (token will be displayed in terminal)
```

### Web Application Development
```bash
# Backend API Server (Express.js + PostgreSQL)
cd web-app/backend
npm install                          # Install dependencies
npm run dev                          # Development server with nodemon
npm start                           # Production server
# API available at: http://localhost:3001

# Frontend React Application (TypeScript + Tailwind CSS)
cd web-app/frontend  
npm install                          # Install dependencies
npm start                           # Development server with hot reload
npm run build                       # Production build
npm test                            # Run test suite
# Frontend available at: http://localhost:3000

# Makefile Development Commands (Recommended)
make dev-web-install                 # Install all dependencies (backend + frontend)
make dev-web-start                   # Start both services in development mode
make dev-web-status                  # Show comprehensive development status
make dev-web-restart                 # Restart both development services

# Web Application Stack Status Check
curl http://localhost:3001/health    # Backend health check
curl http://localhost:3001/api/stocks # Test API endpoint
# Frontend: http://localhost:3000 (React dashboard)

# Comprehensive API Testing (see README.md for full examples with expected results)
curl -s http://localhost:3001/health                                # Health check
curl -s http://localhost:3001/test-db                              # Database connectivity  
curl -s http://localhost:3001/api/stocks                           # All stocks list
curl -s "http://localhost:3001/api/stocks/XTB?timeframe=1M"        # Stock details with OHLCV
curl -s "http://localhost:3001/api/stocks/XTB/analytics?timeframe=3M" # Advanced analytics
curl -s http://localhost:3001/api/models                           # ML model performance
curl -s "http://localhost:3001/api/predictions/XTB?limit=5"        # ML trading signals
curl -s -I http://localhost:3000 | head -5                        # Frontend accessibility
```

## 🧠 Smart Execution Mode Detection (August 2025)

### 4-Layer Intelligent Processing Logic
The ETL DAGs now feature advanced smart detection that automatically chooses the optimal processing strategy:

**Layer 1: Manual Configuration Override** (highest priority)
- Per-instrument overrides: `{"instruments": {"XTB": "historical", "PKN": "incremental"}}`
- Global mode overrides: `{"extraction_mode": "full_backfill"}`

**Layer 2: 🆕 Database State Analysis** (automatic full_backfill detection)
```sql
-- Smart detection automatically analyzes database state:
SELECT COUNT(*) as record_count FROM stock_prices 
WHERE stock_id = (SELECT id FROM base_instruments WHERE symbol = 'XTB')

-- Decision logic:
-- record_count = 0     → full_backfill (unlimited backfill)
-- record_count < 30    → full_backfill (sparse data)  
-- latest_date > 7 days → historical (500-1000 records)
-- current data        → incremental (1 record)
```

**Layer 3: DAG Execution Context**
- Backfill runs → historical mode
- Regular/manual runs → incremental mode

**Layer 4: Safety Default**
- Incremental mode (1 record) for unknown scenarios

### Smart Mode Benefits for New Deployments
**When you run `make start` on a fresh system:**
1. **Database schemas created** but contain 0 stock price records
2. **DAGs triggered automatically** with smart mode detection
3. **Smart mode detects 0 rows** for all instruments
4. **Automatically switches to unlimited full_backfill** without manual intervention
5. **Result: Complete historical data** (50,000+ records) loaded automatically

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

### Web Application Services  
- **Backend API (Express.js)**: http://localhost:3001 - RESTful API with PostgreSQL integration
- **Frontend Dashboard (React)**: http://localhost:3000 - Interactive stock analysis dashboard
- **API Endpoints**: 
  - `GET /api/stocks` - List all stocks with metadata
  - `GET /api/stocks/:symbol` - Detailed stock data with price history  
  - `GET /api/predictions/:symbol` - ML predictions and trading signals
  - `GET /api/models` - ML model performance metrics

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

- **Environment-Specific DAGs**: `dev_stock_etl_pipeline`, `test_stock_etl_pipeline`, `prod_stock_etl_pipeline`
- **Smart Execution Mode Detection**: 4-layer intelligent processing automatically detects backfill vs incremental runs
- **Polish Trading Calendar Integration**: Uses `polish_trading_calendar.py` for market day validation
- **Comprehensive ETL Job Tracking**: Full lifecycle tracking with Airflow context
- **Data Quality Validation**: Automated OHLC validation and anomaly detection
- **Error Handling and Retry Logic**: Graceful failure handling with detailed logging
- **Automated Connections**: postgres_default and postgres_stock connections configured via docker-compose

### ML Pipeline DAG Architecture ✅ WORKING
Dynamic multi-environment ML training DAGs in `stock_etl/airflow_dags/stock_ml_dag.py`:

- **Multi-Environment Support**: Dynamically generated DAGs for each stock symbol per environment (dev/test/prod)
- **Environment-Specific Scheduling**: Manual triggering for dev/test, production schedule for prod
- **7-Day Growth Prediction**: Binary classification for weekly stock growth forecasting
- **Complete ML Pipeline**: Data extraction → feature engineering → model training → backtesting → database storage
- **Schema-Aware Operations**: Each DAG targets its specific environment schema (dev_stock_data, test_stock_data, prod_stock_data)
- **XGBoost Classification**: GPU-accelerated gradient boosting with hyperparameter optimization
- **Environment-Specific Configuration**: Grid search type and model versioning adapted per environment
- **Database Integration**: All ML artifacts stored in environment-specific schemas for web application access

### Environment Configurations
```python
# ETL DAG Environment configurations with smart detection
ENVIRONMENTS = {
    'dev': {
        'schema': 'dev_stock_data',
        'schedule': None,                # Manual triggering with smart detection
        'retries': 1,
        'catchup': False
    },
    'test': {
        'schema': 'test_stock_data',
        'schedule': None,                # Manual triggering with explicit full_backfill
        'retries': 1,
        'catchup': False
    },
    'prod': {
        'schema': 'prod_stock_data',
        'schedule': '0 18 * * 1-5',      # 6 PM weekdays with explicit full_backfill
        'retries': 2,
        'catchup': True
    }
}
```

### DAG Task Flow
1. **check_prerequisites** - Validates trading calendar and execution context with smart mode detection
2. **create_etl_job** - Creates ETL job record with comprehensive metadata
3. **extract_and_transform** - Data extraction with intelligent historical/incremental processing
4. **load_data** - Database loading with detailed per-instrument tracking and incremental commits
5. **validate_data_quality** - Automated quality checks (OHLC, gaps, volumes)
6. **finalize_etl_session** - Job completion with final status and metrics

### Manual DAG Operations
```bash
# Trigger environment-specific DAGs with smart/explicit modes
make trigger-dev-dag     # Smart detection (automatically chooses based on database state)
make trigger-test-dag    # Explicit full_backfill mode (50,000+ records)
make trigger-prod-dag    # Explicit full_backfill mode (50,000+ records)

# Direct Airflow CLI commands
docker-compose exec airflow airflow dags trigger dev_stock_etl_pipeline
docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline --conf '{"extraction_mode": "full_backfill"}'
docker-compose exec airflow airflow dags trigger prod_stock_etl_pipeline --conf '{"extraction_mode": "full_backfill"}'

# ML DAG Operations (dynamic per-stock-environment DAGs)
docker-compose exec airflow airflow dags list | grep ml_pipeline   # List all ML DAGs
docker-compose exec airflow airflow dags trigger test_ml_pipeline_xtb   # Trigger specific stock ML training (test)
docker-compose exec airflow airflow dags trigger prod_ml_pipeline_xtb   # Trigger specific stock ML training (prod)
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
**Stocks**: XTB, PKN, CCC, LPP, CDR, BDX, DVL, ELT, GPW, KTY, PLW, PZU, RBW
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
- All operations tracked in `etl_jobs` table with smart mode decision logging
- Detailed metrics: records processed, inserted, failed
- Integration with Airflow DAG and task IDs
- Incremental commit architecture for enhanced fault tolerance

## Testing Approach

### Test Database
- Use `test_stock_data` schema for testing
- Clean initialization without dummy data
- Isolated from development data

### Validation Strategy
- Pydantic models validate all input data
- OHLC price relationship validation
- Database constraints enforce data integrity
- Hash-based duplicate detection
- Smart mode execution validation

## Web Application Architecture (`web-app/`)

### Full-Stack Architecture
The web application provides an intuitive interface for the stock analysis platform with real-time data integration:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   Backend API   │───▶│  PostgreSQL     │
│  React + TS     │    │   Express.js    │    │ prod_stock_data │
│  Port 3000      │    │   Port 3001     │    │ Port 5432       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Frontend Architecture (`web-app/frontend/`)
- **Framework**: React 18 with TypeScript for type safety
- **Styling**: Tailwind CSS for responsive design and dark/light themes  
- **State Management**: React hooks (useState, useEffect, useMemo) + Context API
- **Key Components**:
  - `src/App.tsx`: Main application with stock dashboard and filtering
  - `src/components/StockDetail.tsx`: Individual stock analysis modal with tabbed interface
  - `src/components/StockComparison.tsx`: Side-by-side stock comparison
  - `src/components/StockFilter.tsx`: Search and sorting functionality
  - `src/components/charts/`: Advanced charting components with Recharts
    - `AdvancedPriceChart.tsx`: Price analysis with moving averages and volume
    - `ReturnsChart.tsx`: Daily returns visualization with statistics
    - `StatisticsChart.tsx`: Comprehensive statistical analysis dashboard
  - `src/components/ui/`: Reusable UI components (Button, Card, Skeleton)
  - `src/hooks/useStockData.ts`: Custom hook for API data fetching

### Backend Architecture (`web-app/backend/`)
- **Framework**: Express.js with TypeScript support
- **Database**: PostgreSQL integration using `pg` driver with connection pooling
- **Security**: CORS middleware, parameterized queries, environment variable configuration
- **Key Endpoints**:
  - `GET /api/stocks` - Stock list with metadata (symbol, name, price, record count)
  - `GET /api/stocks/:symbol?timeframe=3M` - Stock details with OHLCV history
  - `GET /api/stocks/:symbol/analytics?timeframe=3M` - Advanced analytics with technical indicators
  - `GET /api/predictions/:symbol?limit=30` - ML predictions and trading signals  
  - `GET /api/models` - ML model performance metrics (ROC-AUC, accuracy)
  - `GET /health` - Health check endpoint
  - `GET /test-db` - Database connectivity test

### Development Workflow
```bash
# Start complete stack
make start                           # Infrastructure (PostgreSQL + Airflow)
cd web-app/backend && npm run dev    # Backend API (with hot reload)
cd web-app/frontend && npm start     # Frontend React app (with hot reload)

# Development URLs:
# Frontend: http://localhost:3000
# Backend API: http://localhost:3001  
# Database: localhost:5432/stock_data

# Full API testing framework with 10 comprehensive test cases available in README.md
# Includes expected results for all endpoints with real production data
```

## Machine Learning Pipeline (`stock_ml/`)

### ML Architecture Components
- **stock_ml.data_extractor**: Multi-stock data extraction from PostgreSQL with quality filtering
- **stock_ml.feature_engineering**: 180+ TA-Lib technical indicators and physics-inspired features
- **stock_ml.preprocessing**: Data preprocessing with feature selection (no SMOTE - inappropriate for time series)
- **stock_ml.model_trainer_optimized**: GPU-accelerated XGBoost classification with grid search optimization
- **stock_ml.backtesting**: Trading strategy backtesting with performance metrics
- **stock_ml.database_operations**: Complete ML data persistence layer with CRUD operations for all ML tables
- **stock_ml.schema_validator**: Data validation against database schema before insertion
- **stock_ml.test_pipeline**: Comprehensive testing framework for ML pipeline validation
- **stock_ml.logging_config**: Centralized logging utility for consistent ML module logging

### ML Pipeline Flow
1. **Data Extraction**: Multi-stock data from schema with quality filtering
2. **Feature Engineering**: Technical indicators (RSI, MACD, Bollinger Bands, etc.) using TA-Lib
3. **Target Generation**: Binary classification for stock growth prediction (7-30 day forward returns)
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

**Target Variable**: Binary classification for 7-30 day forward stock growth
- Positive class: Stock growth > threshold
- Uses chronological train/validation/test splits (no data leakage)
- Class imbalance handled via `scale_pos_weight` parameter in XGBoost

**Feature Engineering Pipeline**:
- **Price Features**: Returns, log returns, volatility measures
- **Technical Indicators**: RSI, MACD, Bollinger Bands, momentum oscillators
- **Moving Averages**: Multiple timeframes (5, 10, 20, 50, 200 days)
- **Volume Features**: Volume ratios, volume moving averages
- **Market Structure**: Support/resistance levels, trend indicators
- **Physics-Inspired Features**: Chaos theory, thermodynamics, wave physics (180+ total features)

**Model Architecture**:
- **Algorithm**: XGBoost Classifier (GPU-accelerated gradient boosting with native NaN handling)
- **Feature Selection**: Top 25-50 features selected by XGBoost importance
- **Hyperparameter Tuning**: Grid search with cross-validation (quick/comprehensive modes)
- **Validation Strategy**: Time-series aware train/validation/test splits

### ML Quality Thresholds

**Model Performance Criteria**:
- **Minimum ROC-AUC**: 0.55 (better than random)
- **Minimum Accuracy**: 0.52 (accounting for class imbalance)
- **Minimum Win Rate**: 40% (backtesting performance)

**Feature Engineering Quality**:
- **Minimum Records**: 500 trading days per stock
- **Minimum Years**: 2.0 years of data
- **Feature Count**: 25-50 selected features (from 180+ engineered)
- **Missing Values**: < 5% after preprocessing

## Key Design Patterns

### Database Operations
- Connection pooling with SQLAlchemy
- Context managers for session management
- Raw SQL for performance-critical operations
- Schema-aware search path configuration
- Incremental commit architecture for enhanced fault tolerance

### Error Handling
- Comprehensive logging at all levels
- Graceful degradation for data extraction failures
- Retry logic with exponential backoff
- Detailed error tracking in ETL jobs
- Smart mode fallback strategies

### Data Validation
- Multi-layer validation: Pydantic → Database → Business rules
- Automatic type conversion and cleaning
- Price relationship validation (high ≥ open/close ≥ low)
- Trading date and volume validation
- UPSERT logic for idempotent operations

### ML Pipeline Design Patterns
- **Time Series Awareness**: Chronological splits prevent data leakage
- **Feature Engineering**: TA-Lib integration for reliable technical indicators
- **Class Imbalance**: Uses `scale_pos_weight` parameter in XGBoost instead of SMOTE (inappropriate for time series)
- **Model Selection**: XGBoost chosen for superior performance on tabular data and native missing value handling
- **Backtesting Framework**: Walk-forward analysis with realistic trading costs
- **GPU Acceleration**: Automatic hardware detection and optimization

### Web Application Design Patterns
- **Component Architecture**: Modular React components with clear separation of concerns
- **Data Flow**: Unidirectional data flow with React hooks and context API
- **Error Boundaries**: Graceful error handling with descriptive user feedback
- **Type Safety**: Full TypeScript coverage for runtime error prevention
- **State Management**: Local component state with selective global state via Context API
- **API Integration**: Custom hooks for data fetching with loading and error states
- **Chart Architecture**: Reusable chart components with consistent styling and data handling
- **Responsive Design**: Mobile-first approach with Tailwind CSS utility classes

### Operational Design Patterns
- **Environment Separation**: Distinct dev/test/prod environments with isolated data
- **Service Orchestration**: Docker Compose for local development, production-ready containers
- **Configuration Management**: Environment variables with sensible defaults
- **Health Monitoring**: Comprehensive health checks and status reporting
- **Data Preservation vs Clean Restart**: Clear distinction between `docker-restart` (preserves data) and `docker-clean` (deletes data)
- **Smart Mode Detection**: 4-layer intelligent processing for optimal execution strategy

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
- **4-Layer Execution Mode Detection**: Automatically determines optimal processing strategy based on:
  - Manual configuration overrides (highest priority)
  - Database state analysis (0 rows → full_backfill, sparse data → historical, current → incremental)
  - DAG run type (manual, backfill, scheduled)
  - Safety default (incremental mode)
- **ETL Logger**: Enhanced logging with file and console handlers for Airflow
- **Schema Context Management**: Dynamic schema selection from DAG parameters
- **Date Range Validation**: Prevents accidentally huge backfill operations

## Schema Management

### Jinja2 Template System (`sql/schema_template.sql.j2`)
Dynamic schema generation supporting multiple environments:

- **Template Variables**: `schema_name`, `schema_type` (dev/test/prod)
- **Environment-Specific Data**: Test schemas exclude dummy data
- **Comprehensive Schema**: All tables, indexes, functions, and triggers
- **Performance Optimization**: Automatically creates optimized indexes
- **ML Table Integration**: Complete ML pipeline table support

### Key Schema Features
- **Normalized Design**: Separate tables for exchanges, instruments, stocks, indices
- **Timezone Support**: UTC and local timestamps with epoch conversion
- **Data Integrity**: OHLC validation, positive price constraints
- **Performance Indexes**: Optimized for time-series queries and joins
- **ETL Tracking**: Complete job lifecycle and data quality metrics
- **ML Integration**: Seamless storage for models, features, predictions, and backtests

## Production Monitoring & Operations

### ETL Job Performance Monitoring
```sql
-- Recent ETL jobs with smart mode decisions
SELECT job_name, status, records_processed, duration_seconds, started_at,
       metadata->>'execution_config'->>'reason' as execution_reason
FROM etl_jobs 
ORDER BY started_at DESC LIMIT 10;

-- Smart mode effectiveness analysis
SELECT 
    CASE 
        WHEN metadata->>'execution_config'->>'reason' LIKE '%0 records%' THEN 'Auto Full Backfill'
        WHEN metadata->>'execution_config'->>'reason' LIKE '%stale%' THEN 'Auto Historical'
        WHEN metadata->>'execution_config'->>'reason' LIKE '%current%' THEN 'Auto Incremental'
        ELSE 'Manual Override'
    END as mode_type,
    COUNT(*) as job_count,
    ROUND(AVG(records_processed), 0) as avg_records,
    ROUND(AVG(duration_seconds), 2) as avg_duration
FROM etl_jobs 
WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY mode_type;
```

### ML Model Performance Monitoring
```sql
-- ML model performance across environments
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
```

## Recent Enhancements (August 2025)

### Smart Mode Detection
- **4-layer intelligent processing** automatically chooses optimal execution strategy
- **Automatic full_backfill** for fresh deployments (0 rows detected)
- **Database state analysis** prevents manual intervention for new environments
- **Idempotent operations** ensure safe re-execution without duplicates

### ML Pipeline Improvements
- **GPU-accelerated XGBoost** with automatic hardware detection
- **Multi-environment ML DAGs** with schema separation (test/prod)
- **180+ physics-inspired features** including chaos theory and thermodynamics
- **Grid search optimization** with quick (192 params) vs comprehensive (12,800 params) modes

### Web Application Integration
- **Production-ready React dashboard** with real-time stock data
- **Advanced charting** with technical indicators and statistical analysis
- **Complete API framework** with 10 comprehensive test cases
- **Docker integration** with main infrastructure deployment

### Infrastructure Enhancements
- **Incremental commit architecture** for enhanced fault tolerance
- **Enhanced duplicate prevention** with validation across multiple runs
- **Automated credential management** with service orchestration
- **Complete Docker integration** for web application deployment

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.