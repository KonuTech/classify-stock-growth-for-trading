-- Development Schema
-- PostgreSQL 17+ compatible with timezone and epoch support

DROP SCHEMA IF EXISTS dev_stock_data CASCADE;
CREATE SCHEMA IF NOT EXISTS dev_stock_data;
SET search_path TO dev_stock_data, public;
-- Create enums (same as test)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'instrument_type' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'dev_stock_data')) THEN
        CREATE TYPE dev_stock_data.instrument_type AS ENUM ('stock', 'index', 'etf', 'bond', 'future', 'option');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'exchange_code' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'dev_stock_data')) THEN
        CREATE TYPE dev_stock_data.exchange_code AS ENUM ('WSE', 'NewConnect', 'Catalyst', 'BondSpot', 'NYSE', 'NASDAQ', 'LSE');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'job_status' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'dev_stock_data')) THEN
        CREATE TYPE dev_stock_data.job_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled', 'retrying');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'severity_level' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'dev_stock_data')) THEN
        CREATE TYPE dev_stock_data.severity_level AS ENUM ('info', 'warning', 'error', 'critical');
    END IF;
END $$;

-- Countries table
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    iso_code VARCHAR(3) NOT NULL UNIQUE,
    currency_code VARCHAR(3) NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT
);

-- Exchanges table
CREATE TABLE IF NOT EXISTS exchanges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    mic_code VARCHAR(4) NOT NULL UNIQUE,
    country_id INTEGER NOT NULL REFERENCES countries(id),
    timezone VARCHAR(50) NOT NULL,
    market_open TIME NOT NULL,
    market_close TIME NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT
);

-- Sectors table
CREATE TABLE IF NOT EXISTS sectors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(500),
    classification_system VARCHAR(50) NOT NULL DEFAULT 'GICS',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT
);

-- Base instruments table
CREATE TABLE IF NOT EXISTS base_instruments (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    instrument_type instrument_type NOT NULL,
    exchange_id INTEGER NOT NULL REFERENCES exchanges(id),
    currency VARCHAR(3) NOT NULL DEFAULT 'PLN',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    first_trading_date DATE,
    last_trading_date DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT,
    
    CONSTRAINT unique_symbol_exchange UNIQUE (symbol, exchange_id)
);

-- Stocks table
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    instrument_id INTEGER NOT NULL REFERENCES base_instruments(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    sector_id INTEGER REFERENCES sectors(id),
    market_cap BIGINT,
    shares_outstanding BIGINT,
    dividend_yield DECIMAL(5,4),
    pe_ratio DECIMAL(8,2),
    book_value DECIMAL(8,2),
    stock_type VARCHAR(10) NOT NULL DEFAULT 'common',
    
    CONSTRAINT unique_stock_instrument UNIQUE (instrument_id)
);

-- Indices table
CREATE TABLE IF NOT EXISTS indices (
    id SERIAL PRIMARY KEY,
    instrument_id INTEGER NOT NULL REFERENCES base_instruments(id) ON DELETE CASCADE,
    methodology VARCHAR(100) NOT NULL DEFAULT 'market_cap_weighted',
    base_value DECIMAL(15,6) NOT NULL,
    base_date DATE NOT NULL,
    constituent_count INTEGER,
    calculation_frequency VARCHAR(20) NOT NULL DEFAULT 'real_time',
    index_family VARCHAR(100),
    
    CONSTRAINT unique_index_instrument UNIQUE (instrument_id)
);

-- Stock prices table
CREATE TABLE IF NOT EXISTS stock_prices (
    id BIGSERIAL PRIMARY KEY,
    stock_id INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    trading_date_local DATE NOT NULL,
    trading_date_utc DATE NOT NULL,
    trading_date_epoch BIGINT NOT NULL,
    trading_datetime_utc TIMESTAMP WITH TIME ZONE,
    trading_datetime_epoch BIGINT,
    open_price DECIMAL(15,6) NOT NULL,
    high_price DECIMAL(15,6) NOT NULL,
    low_price DECIMAL(15,6) NOT NULL,
    close_price DECIMAL(15,6) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    adjusted_close DECIMAL(15,6),
    split_factor DECIMAL(8,4) DEFAULT 1.0,
    dividend_amount DECIMAL(8,4) DEFAULT 0.0,
    data_source VARCHAR(50) NOT NULL DEFAULT 'stooq',
    raw_data_hash VARCHAR(64), -- For detecting duplicate imports
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT,
    
    CONSTRAINT unique_stock_date UNIQUE (stock_id, trading_date_local),
    CONSTRAINT positive_prices CHECK (open_price >= 0 AND high_price >= 0 AND low_price >= 0 AND close_price >= 0),
    CONSTRAINT valid_ohlc CHECK (high_price >= open_price AND high_price >= close_price AND 
                                 low_price <= open_price AND low_price <= close_price)
);

-- Index prices table
CREATE TABLE IF NOT EXISTS index_prices (
    id BIGSERIAL PRIMARY KEY,
    index_id INTEGER NOT NULL REFERENCES indices(id) ON DELETE CASCADE,
    trading_date_local DATE NOT NULL,
    trading_date_utc DATE NOT NULL,
    trading_date_epoch BIGINT NOT NULL,
    trading_datetime_utc TIMESTAMP WITH TIME ZONE,
    trading_datetime_epoch BIGINT,
    open_value DECIMAL(15,6) NOT NULL,
    high_value DECIMAL(15,6) NOT NULL,
    low_value DECIMAL(15,6) NOT NULL,
    close_value DECIMAL(15,6) NOT NULL,
    trading_volume BIGINT NOT NULL DEFAULT 0,
    total_market_cap DECIMAL(20,2),
    constituents_traded INTEGER,
    data_source VARCHAR(50) NOT NULL DEFAULT 'stooq',
    raw_data_hash VARCHAR(64), -- For detecting duplicate imports
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT,
    
    CONSTRAINT unique_index_date UNIQUE (index_id, trading_date_local),
    CONSTRAINT positive_values CHECK (open_value >= 0 AND high_value >= 0 AND low_value >= 0 AND close_value >= 0)
);

-- ETL jobs table
CREATE TABLE IF NOT EXISTS etl_jobs (
    id BIGSERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    target_instrument_type instrument_type,
    status job_status NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    started_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT,
    completed_at TIMESTAMP WITH TIME ZONE,
    completed_at_epoch BIGINT,
    duration_seconds INTEGER,
    records_processed INTEGER NOT NULL DEFAULT 0,
    records_inserted INTEGER NOT NULL DEFAULT 0,
    records_updated INTEGER NOT NULL DEFAULT 0,
    records_failed INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    source_files TEXT[], -- Array of source files processed
    target_date_range_start DATE,
    target_date_range_end DATE,
    airflow_dag_id VARCHAR(100),
    airflow_task_id VARCHAR(100),
    airflow_run_id VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT
);

-- ETL job details table
CREATE TABLE IF NOT EXISTS etl_job_details (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES etl_jobs(id) ON DELETE CASCADE,
    instrument_id INTEGER REFERENCES base_instruments(id) ON DELETE CASCADE,
    operation VARCHAR(20) NOT NULL,
    date_processed DATE NOT NULL,
    date_processed_epoch BIGINT NOT NULL,
    records_count INTEGER NOT NULL DEFAULT 1,
    file_processed VARCHAR(500),
    line_number INTEGER,
    error_details TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT
);

-- Data quality metrics table
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT REFERENCES etl_jobs(id) ON DELETE SET NULL,
    instrument_id INTEGER NOT NULL REFERENCES base_instruments(id) ON DELETE CASCADE,
    instrument_type instrument_type NOT NULL,
    metric_date DATE NOT NULL,
    metric_date_epoch BIGINT NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6),
    threshold_min DECIMAL(15,6),
    threshold_max DECIMAL(15,6),
    is_valid BOOLEAN NOT NULL,
    severity severity_level NOT NULL DEFAULT 'info',
    description TEXT,
    automated_check BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT,
    
    CONSTRAINT unique_instrument_date_metric UNIQUE (instrument_id, metric_date, metric_name)
);

-- Data sources table
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    base_url VARCHAR(500),
    source_type VARCHAR(50) NOT NULL DEFAULT 'api',
    api_key_required BOOLEAN NOT NULL DEFAULT FALSE,
    rate_limit_per_minute INTEGER,
    data_format VARCHAR(50) NOT NULL DEFAULT 'csv',
    default_timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_successful_fetch TIMESTAMP WITH TIME ZONE,
    last_successful_fetch_epoch BIGINT,
    total_fetches INTEGER NOT NULL DEFAULT 0,
    failed_fetches INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_epoch BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT
);

-- Create performance-optimized indexes
DO $$
BEGIN
    -- Countries indexes
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_countries_iso_code ON countries(iso_code)';
    
    -- Exchanges indexes
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_exchanges_country_id ON exchanges(country_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_exchanges_active ON exchanges(is_active)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_exchanges_mic_code ON exchanges(mic_code)';
    
    -- Sectors indexes
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_sectors_name ON sectors(name)';
    
    -- Base instruments indexes (critical for joins)
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_base_instruments_symbol ON base_instruments(symbol)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_base_instruments_type ON base_instruments(instrument_type)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_base_instruments_exchange ON base_instruments(exchange_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_base_instruments_active ON base_instruments(is_active)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_base_instruments_symbol_type ON base_instruments(symbol, instrument_type)';
    
    -- Stocks indexes
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stocks_instrument_id ON stocks(instrument_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stocks_sector_id ON stocks(sector_id)';
    
    -- Indices indexes
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_indices_instrument_id ON indices(instrument_id)';
    
    -- Stock prices indexes (high-performance queries)
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stock_prices_stock_id ON stock_prices(stock_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(trading_date_local)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stock_prices_stock_date ON stock_prices(stock_id, trading_date_local DESC)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stock_prices_date_epoch ON stock_prices(trading_date_epoch)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stock_prices_source ON stock_prices(data_source)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_stock_prices_hash ON stock_prices(raw_data_hash)';
    
    -- Index prices indexes (high-performance queries)
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_index_prices_index_id ON index_prices(index_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_index_prices_date ON index_prices(trading_date_local)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_index_prices_index_date ON index_prices(index_id, trading_date_local DESC)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_index_prices_date_epoch ON index_prices(trading_date_epoch)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_index_prices_source ON index_prices(data_source)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_index_prices_hash ON index_prices(raw_data_hash)';
    
    -- ETL jobs indexes
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_etl_jobs_status ON etl_jobs(status)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_etl_jobs_type ON etl_jobs(job_type)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_etl_jobs_started_epoch ON etl_jobs(started_at_epoch)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_etl_jobs_dag_run ON etl_jobs(airflow_dag_id, airflow_run_id)';
    
    -- ETL job details indexes  
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_etl_job_details_job_id ON etl_job_details(job_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_etl_job_details_date_epoch ON etl_job_details(date_processed_epoch)';
    
    -- Data quality metrics indexes
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_instrument ON data_quality_metrics(instrument_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_date ON data_quality_metrics(metric_date)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_data_quality_invalid ON data_quality_metrics(is_valid) WHERE is_valid = FALSE';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_data_quality_metrics_severity ON data_quality_metrics(severity)';
END $$;

-- Create helper functions
CREATE OR REPLACE FUNCTION calculate_date_epoch(date_val DATE, tz VARCHAR DEFAULT 'UTC')
RETURNS BIGINT 
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    RETURN EXTRACT(EPOCH FROM (date_val::TIMESTAMP AT TIME ZONE tz))::BIGINT;
END;
$$;

CREATE OR REPLACE FUNCTION update_timestamp_and_epoch_columns()
RETURNS TRIGGER 
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.updated_at_epoch = EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT;
    RETURN NEW;
END;
$$;

-- Create function to calculate data hash for duplicate detection
CREATE OR REPLACE FUNCTION calculate_stooq_data_hash(
    p_symbol VARCHAR(20),
    p_date DATE,
    p_open DECIMAL(15,6),
    p_high DECIMAL(15,6),
    p_low DECIMAL(15,6),
    p_close DECIMAL(15,6),
    p_volume DECIMAL(20,6)
)
RETURNS VARCHAR(64)
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    RETURN encode(sha256((p_symbol || p_date || p_open || p_high || p_low || p_close || p_volume)::bytea), 'hex');
END;
$$;

-- Create triggers
DO $$
BEGIN
    DROP TRIGGER IF EXISTS update_base_instruments_timestamp_epoch ON base_instruments;
    CREATE TRIGGER update_base_instruments_timestamp_epoch 
        BEFORE UPDATE ON base_instruments 
        FOR EACH ROW EXECUTE FUNCTION update_timestamp_and_epoch_columns();
    
    DROP TRIGGER IF EXISTS update_data_sources_timestamp_epoch ON data_sources;
    CREATE TRIGGER update_data_sources_timestamp_epoch 
        BEFORE UPDATE ON data_sources 
        FOR EACH ROW EXECUTE FUNCTION update_timestamp_and_epoch_columns();
END $$;