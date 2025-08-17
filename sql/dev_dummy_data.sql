-- Insert dummy data for development schema (normalized approach)
-- This populates the development environment with sample data for testing

SET search_path TO dev_stock_data, public;

-- Insert dummy data using PL/pgSQL for better control
DO $$
DECLARE
    v_poland_id INTEGER;
    v_wse_id INTEGER;
    v_financial_sector_id INTEGER;
    v_energy_sector_id INTEGER;
    v_xtb_instrument_id INTEGER;
    v_wig_instrument_id INTEGER;
    v_pkn_instrument_id INTEGER;
    v_xtb_stock_id INTEGER;
    v_wig_index_id INTEGER;
    v_pkn_stock_id INTEGER;
    v_job_id BIGINT;
    v_date DATE;
    v_price DECIMAL(15,6);
    v_index_value DECIMAL(15,6);
    v_utc_datetime TIMESTAMP WITH TIME ZONE;
    v_open DECIMAL(15,6);
    v_high DECIMAL(15,6);
    v_low DECIMAL(15,6);
    v_close DECIMAL(15,6);
    i INTEGER;
BEGIN
    -- Insert countries
    INSERT INTO countries (name, iso_code, currency_code, timezone) 
    VALUES ('Poland', 'POL', 'PLN', 'Europe/Warsaw')
    ON CONFLICT (iso_code) DO NOTHING
    RETURNING id INTO v_poland_id;
    
    IF v_poland_id IS NULL THEN
        SELECT id INTO v_poland_id FROM countries WHERE iso_code = 'POL';
    END IF;
    
    -- Insert exchanges
    INSERT INTO exchanges (name, mic_code, country_id, timezone, market_open, market_close, is_active)
    VALUES ('Warsaw Stock Exchange', 'XWAR', v_poland_id, 'Europe/Warsaw', '09:00:00', '17:00:00', TRUE)
    ON CONFLICT (mic_code) DO NOTHING
    RETURNING id INTO v_wse_id;
    
    IF v_wse_id IS NULL THEN
        SELECT id INTO v_wse_id FROM exchanges WHERE mic_code = 'XWAR';
    END IF;
    
    -- Insert sectors
    INSERT INTO sectors (name, description, classification_system)
    VALUES 
        ('Financial Services', 'Banks, brokerages, insurance companies', 'GICS'),
        ('Energy', 'Oil, gas, renewable energy companies', 'GICS'),
        ('Technology', 'Software, hardware, IT services', 'GICS')
    ON CONFLICT (name) DO NOTHING;
    
    SELECT id INTO v_financial_sector_id FROM sectors WHERE name = 'Financial Services';
    SELECT id INTO v_energy_sector_id FROM sectors WHERE name = 'Energy';
    
    -- Insert data sources
    INSERT INTO data_sources (name, base_url, data_format, rate_limit_per_minute, default_timezone) 
    VALUES ('stooq', 'https://stooq.com/q/d/l/', 'csv', 60, 'Europe/Warsaw')
    ON CONFLICT (name) DO NOTHING;
    
    -- Insert base instruments
    INSERT INTO base_instruments (symbol, name, instrument_type, exchange_id, currency, is_active, first_trading_date)
    VALUES 
        ('XTB', 'X-Trade Brokers Dom Maklerski S.A.', 'stock', v_wse_id, 'PLN', TRUE, '2016-05-06'),
        ('WIG', 'WIG Index', 'index', v_wse_id, 'PLN', TRUE, '1991-04-16'),
        ('PKN', 'PKN Orlen S.A.', 'stock', v_wse_id, 'PLN', TRUE, '1999-11-25')
    ON CONFLICT (symbol, exchange_id) DO NOTHING;
    
    -- Get instrument IDs
    SELECT id INTO v_xtb_instrument_id FROM base_instruments WHERE symbol = 'XTB' AND exchange_id = v_wse_id;
    SELECT id INTO v_wig_instrument_id FROM base_instruments WHERE symbol = 'WIG' AND exchange_id = v_wse_id;
    SELECT id INTO v_pkn_instrument_id FROM base_instruments WHERE symbol = 'PKN' AND exchange_id = v_wse_id;
    
    -- Insert stocks
    INSERT INTO stocks (instrument_id, company_name, sector_id, market_cap, shares_outstanding, dividend_yield, pe_ratio, stock_type)
    VALUES 
        (v_xtb_instrument_id, 'X-Trade Brokers Dom Maklerski S.A.', v_financial_sector_id, 2500000000, 150000000, 0.0250, 12.5, 'common'),
        (v_pkn_instrument_id, 'PKN Orlen S.A.', v_energy_sector_id, 45000000000, 586000000, 0.0580, 8.3, 'common')
    ON CONFLICT DO NOTHING;
    
    -- Insert indices
    INSERT INTO indices (instrument_id, methodology, base_value, base_date, constituent_count, calculation_frequency, index_family)
    VALUES 
        (v_wig_instrument_id, 'market_cap_weighted', 1000.0, '1991-04-16', 400, 'real_time', 'WIG')
    ON CONFLICT DO NOTHING;
    
    -- Get stock and index IDs
    SELECT id INTO v_xtb_stock_id FROM stocks WHERE instrument_id = v_xtb_instrument_id;
    SELECT id INTO v_wig_index_id FROM indices WHERE instrument_id = v_wig_instrument_id;
    SELECT id INTO v_pkn_stock_id FROM stocks WHERE instrument_id = v_pkn_instrument_id;
    
    -- Generate dummy price data for last 30 days
    FOR i IN 0..29 LOOP
        v_date := CURRENT_DATE - INTERVAL '1 day' * i;
        v_utc_datetime := (v_date || ' 15:30:00')::TIMESTAMP AT TIME ZONE 'Europe/Warsaw' AT TIME ZONE 'UTC';
        
        -- XTB stock data (trending upward with volatility)
        v_price := 6.50 + (i * 0.05) + (random() * 0.30 - 0.15);
        IF v_price < 0.1 THEN v_price := 0.1; END IF;
        
        -- Generate OHLC with proper relationships
        v_open := v_price;
        v_high := v_price * (1 + random() * 0.03);
        v_low := v_price * (1 - random() * 0.03);
        v_close := v_price * (1 + (random() * 0.04 - 0.02));
        
        -- Ensure High is the maximum and Low is the minimum
        v_high := GREATEST(v_open, v_high, v_close);
        v_low := LEAST(v_open, v_low, v_close);
        
        INSERT INTO stock_prices (
            stock_id, trading_date_local, trading_date_utc, trading_date_epoch,
            trading_datetime_utc, trading_datetime_epoch,
            open_price, high_price, low_price, close_price, volume, adjusted_close
        ) VALUES (
            v_xtb_stock_id, v_date, v_date, calculate_date_epoch(v_date, 'Europe/Warsaw'),
            v_utc_datetime, EXTRACT(EPOCH FROM v_utc_datetime)::BIGINT,
            v_open, v_high, v_low, v_close,
            (500000 + random() * 1000000)::BIGINT, v_close
        ) ON CONFLICT (stock_id, trading_date_local) DO NOTHING;
        
        -- PKN stock data (more volatile energy stock)
        v_price := 85.0 + (random() * 15 - 7.5);
        IF v_price < 1.0 THEN v_price := 1.0; END IF;
        
        -- Generate OHLC with proper relationships for PKN
        v_open := v_price;
        v_high := v_price * (1 + random() * 0.04);
        v_low := v_price * (1 - random() * 0.04);
        v_close := v_price * (1 + (random() * 0.06 - 0.03));
        
        -- Ensure High is the maximum and Low is the minimum
        v_high := GREATEST(v_open, v_high, v_close);
        v_low := LEAST(v_open, v_low, v_close);
        
        INSERT INTO stock_prices (
            stock_id, trading_date_local, trading_date_utc, trading_date_epoch,
            trading_datetime_utc, trading_datetime_epoch,
            open_price, high_price, low_price, close_price, volume, adjusted_close
        ) VALUES (
            v_pkn_stock_id, v_date, v_date, calculate_date_epoch(v_date, 'Europe/Warsaw'),
            v_utc_datetime, EXTRACT(EPOCH FROM v_utc_datetime)::BIGINT,
            v_open, v_high, v_low, v_close,
            (800000 + random() * 1500000)::BIGINT, v_close
        ) ON CONFLICT (stock_id, trading_date_local) DO NOTHING;
        
        -- WIG index data (more stable, trending upward slowly)
        v_index_value := 75000 + (i * 100) + (random() * 800 - 400);
        IF v_index_value < 1000 THEN v_index_value := 1000; END IF;
        
        -- Generate OHLC with proper relationships for WIG index
        v_open := v_index_value;
        v_high := v_index_value * (1 + random() * 0.01);
        v_low := v_index_value * (1 - random() * 0.01);
        v_close := v_index_value * (1 + (random() * 0.02 - 0.01));
        
        -- Ensure High is the maximum and Low is the minimum
        v_high := GREATEST(v_open, v_high, v_close);
        v_low := LEAST(v_open, v_low, v_close);
        
        INSERT INTO index_prices (
            index_id, trading_date_local, trading_date_utc, trading_date_epoch,
            trading_datetime_utc, trading_datetime_epoch,
            open_value, high_value, low_value, close_value, trading_volume, total_market_cap
        ) VALUES (
            v_wig_index_id, v_date, v_date, calculate_date_epoch(v_date, 'Europe/Warsaw'),
            v_utc_datetime, EXTRACT(EPOCH FROM v_utc_datetime)::BIGINT,
            v_open, v_high, v_low, v_close,
            (15000 + random() * 35000)::BIGINT, 750000000000::DECIMAL(20,2)
        ) ON CONFLICT (index_id, trading_date_local) DO NOTHING;
        
    END LOOP;
    
    -- Insert sample ETL job
    INSERT INTO etl_jobs (
        job_name, job_type, target_instrument_type, status, 
        started_at, completed_at, records_processed, records_inserted, metadata
    ) VALUES (
        'dev_dummy_data_load', 'historical_backfill', 'stock', 'completed', 
        CURRENT_TIMESTAMP - INTERVAL '2 hours', CURRENT_TIMESTAMP - INTERVAL '1 hour',
        90, 90, 
        '{"source": "dummy_data_generator", "instruments": ["XTB", "PKN", "WIG"], "date_range": "30_days"}'::JSONB
    ) RETURNING id INTO v_job_id;
    
    -- Insert sample ETL job details
    INSERT INTO etl_job_details (
        job_id, instrument_id, operation, date_processed, date_processed_epoch, records_count
    ) VALUES 
        (v_job_id, v_xtb_instrument_id, 'insert', CURRENT_DATE, calculate_date_epoch(CURRENT_DATE), 30),
        (v_job_id, v_pkn_instrument_id, 'insert', CURRENT_DATE, calculate_date_epoch(CURRENT_DATE), 30),
        (v_job_id, v_wig_instrument_id, 'insert', CURRENT_DATE, calculate_date_epoch(CURRENT_DATE), 30);
    
    -- Insert sample data quality metrics
    INSERT INTO data_quality_metrics (
        job_id, instrument_id, instrument_type, metric_date, metric_date_epoch,
        metric_name, metric_value, is_valid, severity, description
    ) VALUES 
        (v_job_id, v_xtb_instrument_id, 'stock', CURRENT_DATE, calculate_date_epoch(CURRENT_DATE), 
         'price_gap_check', 0.05, TRUE, 'info', 'Normal price gap within acceptable range'),
        (v_job_id, v_wig_instrument_id, 'index', CURRENT_DATE, calculate_date_epoch(CURRENT_DATE), 
         'volume_consistency', 25000, TRUE, 'info', 'Trading volume within expected range'),
        (v_job_id, v_pkn_instrument_id, 'stock', CURRENT_DATE - 1, calculate_date_epoch(CURRENT_DATE - 1), 
         'volatility_spike', 6.2, FALSE, 'warning', 'Unusual volatility detected - price movement > 5%');
    
    RAISE NOTICE 'Development dummy data inserted successfully';
    RAISE NOTICE 'Instruments created: XTB (stock), PKN (stock), WIG (index)';
    RAISE NOTICE 'Price data: 30 days of dummy data for each instrument';
    RAISE NOTICE 'ETL tracking: Sample job with % records processed', 90;
    
END $$;