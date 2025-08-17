# ERD: Unified Approach (Expert A)

## Database Schema Overview
This diagram shows the unified table design where stocks and indices share the same table structure with `instrument_type` discriminator.

```mermaid
erDiagram
    instruments ||--o{ daily_prices : "has many"
    instruments ||--o{ etl_job_details : "processed in"
    instruments ||--o{ data_quality_metrics : "has metrics for"
    data_sources ||--o{ etl_jobs : "sources data for"
    etl_jobs ||--o{ etl_job_details : "contains"
    
    instruments {
        SERIAL id PK
        VARCHAR(20) ticker
        VARCHAR(255) name
        instrument_type instrument_type "stock/index/etf/etc"
        exchange_code exchange
        VARCHAR(50) exchange_timezone
        VARCHAR(100) sector
        VARCHAR(100) industry
        VARCHAR(20) market_cap_category
        BOOLEAN is_active
        DATE first_trading_date
        DATE last_trading_date
        VARCHAR(3) currency
        TIMESTAMPTZ created_at
        BIGINT created_at_epoch
        TIMESTAMPTZ updated_at
        BIGINT updated_at_epoch
    }
    
    daily_prices {
        BIGSERIAL id PK
        INTEGER instrument_id FK
        VARCHAR(20) ticker "denormalized"
        instrument_type instrument_type "denormalized"
        VARCHAR(5) period
        DATE trading_date_local
        TIMESTAMPTZ trading_datetime_local
        VARCHAR(50) exchange_timezone
        DATE trading_date_utc
        TIMESTAMPTZ trading_datetime_utc
        BIGINT trading_date_epoch
        BIGINT trading_datetime_epoch
        DECIMAL_15_6 open_price
        DECIMAL_15_6 high_price
        DECIMAL_15_6 low_price
        DECIMAL_15_6 close_price
        DECIMAL_20_6 volume
        DECIMAL_20_6 open_interest
        TIMESTAMPTZ created_at
        BIGINT created_at_epoch
        TIMESTAMPTZ updated_at
        BIGINT updated_at_epoch
    }
    
    etl_jobs {
        BIGSERIAL id PK
        VARCHAR(100) job_name
        VARCHAR(50) job_type
        instrument_type instrument_type
        job_status status
        TIMESTAMPTZ started_at
        BIGINT started_at_epoch
        TIMESTAMPTZ completed_at
        BIGINT completed_at_epoch
        INTEGER duration_seconds
        INTEGER records_processed
        INTEGER records_inserted
        INTEGER records_updated
        INTEGER records_failed
        TEXT error_message
        INTEGER error_count
        INTEGER retry_count
        INTEGER max_retries
        VARCHAR(500) source_file
        TEXT[] target_tickers
        JSONB metadata
        TIMESTAMPTZ created_at
        BIGINT created_at_epoch
    }
    
    etl_job_details {
        BIGSERIAL id PK
        BIGINT job_id FK
        INTEGER instrument_id FK
        VARCHAR(20) ticker
        VARCHAR(20) operation
        DATE date_processed
        BIGINT date_processed_epoch
        INTEGER records_count
        TEXT error_details
        INTEGER processing_time_ms
        TIMESTAMPTZ created_at
        BIGINT created_at_epoch
    }
    
    data_quality_metrics {
        BIGSERIAL id PK
        BIGINT job_id FK
        INTEGER instrument_id FK
        VARCHAR(20) ticker
        instrument_type instrument_type
        DATE date
        BIGINT date_epoch
        VARCHAR(100) metric_name
        DECIMAL_15_6 metric_value
        DECIMAL_15_6 expected_min
        DECIMAL_15_6 expected_max
        BOOLEAN is_valid
        severity_level severity
        TEXT description
        TIMESTAMPTZ created_at
        BIGINT created_at_epoch
    }
    
    data_sources {
        SERIAL id PK
        VARCHAR(100) name
        VARCHAR(500) base_url
        BOOLEAN api_key_required
        INTEGER rate_limit_per_minute
        VARCHAR(50) data_format
        VARCHAR(50) default_timezone
        BOOLEAN is_active
        TIMESTAMPTZ last_successful_fetch
        BIGINT last_successful_fetch_epoch
        TIMESTAMPTZ created_at
        BIGINT created_at_epoch
        TIMESTAMPTZ updated_at
        BIGINT updated_at_epoch
    }
```

## Key Benefits of Unified Approach

### Performance Advantages
- **Single Table Queries**: All price data in one table enables fast cross-instrument analysis
- **Optimized Indexing**: Composite indexes on `(ticker, trading_date_local)` serve all queries
- **Reduced JOIN Complexity**: No need for UNION operations across stock/index tables
- **Memory Locality**: Related data (stocks and indices) in same table pages

### Operational Benefits
- **Simplified ETL**: One pipeline handles all instrument types
- **Consistent Schema**: Same validation rules and constraints across all instruments
- **Easy Maintenance**: Single backup/recovery strategy
- **Unified Analytics**: Cross-asset correlation analysis in single queries

### Example Queries
```sql
-- Compare stock performance against index
SELECT 
    s.ticker as stock,
    i.ticker as index,
    s.close_price / LAG(s.close_price) OVER (ORDER BY s.trading_date_local) - 1 as stock_return,
    i.close_price / LAG(i.close_price) OVER (ORDER BY i.trading_date_local) - 1 as index_return
FROM daily_prices s
JOIN daily_prices i ON s.trading_date_local = i.trading_date_local
WHERE s.ticker = 'XTB' AND i.ticker = 'WIG'
ORDER BY s.trading_date_local;

-- Sector performance analysis
SELECT 
    i.sector,
    AVG(dp.close_price / LAG(dp.close_price) OVER (PARTITION BY dp.ticker ORDER BY dp.trading_date_local) - 1) as avg_return
FROM instruments i
JOIN daily_prices dp ON i.id = dp.instrument_id
WHERE i.instrument_type = 'stock'
    AND dp.trading_date_local >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY i.sector;
```

## Index Strategy
```sql
-- Critical indexes for performance
CREATE INDEX idx_daily_prices_ticker_date ON daily_prices(ticker, trading_date_local);
CREATE INDEX idx_daily_prices_instrument_date ON daily_prices(instrument_id, trading_date_local);
CREATE INDEX idx_daily_prices_type_date ON daily_prices(instrument_type, trading_date_local DESC);
CREATE INDEX idx_instruments_type_active ON instruments(instrument_type, is_active);
```