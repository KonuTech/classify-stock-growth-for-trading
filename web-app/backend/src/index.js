const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { Pool } = require('pg');
const cacheManager = require('./cache');

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

// Database connection
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'stock_data',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
});

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Simple database test endpoint
app.get('/test-db', async (req, res) => {
  try {
    console.log('🧪 Testing basic database connection...');
    const result = await pool.query('SELECT 1 as test');
    console.log('✅ Basic connection works');
    
    const schemaTest = await pool.query('SET search_path TO prod_stock_data');
    console.log('✅ Schema path set');
    
    const countResult = await pool.query('SELECT COUNT(*) as count FROM base_instruments');
    console.log('✅ Table query works, count:', countResult.rows[0].count);
    
    res.json({ 
      status: 'Database connection OK', 
      instrumentCount: countResult.rows[0].count 
    });
  } catch (error) {
    console.error('❌ Database test failed:', error);
    res.status(500).json({ error: 'Database test failed', details: error.message });
  }
});

// Get all stocks with basic statistics
app.get('/api/stocks', async (req, res) => {
  const { timeframe = '1Y' } = req.query;
  console.log(`📊 Fetching stocks with statistics from prod_stock_data (timeframe: ${timeframe})...`);
  
  // Check cache first
  const cacheKey = cacheManager.getStockListKey(timeframe);
  const cachedData = await cacheManager.get(cacheKey);
  
  if (cachedData) {
    console.log(`⚡ Returning cached data for timeframe: ${timeframe} (${cachedData.length} stocks)`);
    return res.json(cachedData);
  }
  
  // Calculate date range based on timeframe
  let daysBack;
  let useTimeframeFilter = true;
  switch(timeframe) {
    case '1M': daysBack = 30; break;
    case '3M': daysBack = 90; break;
    case '6M': daysBack = 180; break;
    case '1Y': daysBack = 365; break;
    case 'MAX': 
      useTimeframeFilter = false; 
      daysBack = null;
      break;
    default: daysBack = 365;
  }
  
  const startTime = Date.now();
  console.log(`🔍 Cache MISS - Computing fresh statistics for ${timeframe} timeframe...`);
  
  try {
    // Test basic connection first
    const testResult = await pool.query('SELECT 1 as test');
    console.log('✅ Database connection working');
    
    await pool.query('SET search_path TO prod_stock_data');
    console.log('✅ Search path set to prod_stock_data');
    
    // Build the query dynamically based on whether we're filtering by timeframe
    let query, params;
    
    if (useTimeframeFilter) {
      query = `
        WITH stock_stats AS (
          SELECT 
            bi.id,
            bi.symbol,
            bi.name,
            bi.currency,
            COUNT(sp.id) as total_records,
            MAX(sp.trading_date_local) as latest_date,
            -- Current price (latest)
            (SELECT sp2.close_price 
             FROM stock_prices sp2 
             WHERE sp2.stock_id = bi.id 
             ORDER BY sp2.trading_date_local DESC 
             LIMIT 1) as current_price,
            -- First price for total return calculation (within timeframe)
            (SELECT sp3.close_price 
             FROM stock_prices sp3 
             WHERE sp3.stock_id = bi.id 
               AND sp3.trading_date_local >= CURRENT_DATE - INTERVAL '1 day' * $3
             ORDER BY sp3.trading_date_local ASC 
             LIMIT 1) as first_price,
            -- Price range (high and low)
            MAX(sp.high_price) as highest_price,
            MIN(sp.low_price) as lowest_price
          FROM base_instruments bi
          LEFT JOIN stock_prices sp ON bi.id = sp.stock_id
            AND sp.trading_date_local >= CURRENT_DATE - INTERVAL '1 day' * $3
          WHERE bi.instrument_type = $1 AND bi.is_active = $2
          GROUP BY bi.id, bi.symbol, bi.name, bi.currency
        ),
        daily_returns AS (
          SELECT 
            ss.id,
            ss.symbol,
            AVG(
              CASE 
                WHEN prev_close.close_price IS NOT NULL AND prev_close.close_price > 0 
                THEN ((sp.close_price - prev_close.close_price) / prev_close.close_price) * 100 
                ELSE NULL 
              END
            ) as avg_daily_return
          FROM stock_stats ss
          LEFT JOIN stock_prices sp ON ss.id = sp.stock_id
            AND sp.trading_date_local >= CURRENT_DATE - INTERVAL '1 day' * $3
          LEFT JOIN stock_prices prev_close ON ss.id = prev_close.stock_id 
            AND prev_close.trading_date_local = sp.trading_date_local - INTERVAL '1 day'
          GROUP BY ss.id, ss.symbol
        ),
        drawdown_calc AS (
          SELECT 
            ss.id,
            ss.symbol,
            -- Calculate running maximum and drawdown
            MIN(
              CASE 
                WHEN running_max.max_price > 0 
                THEN ((sp.close_price - running_max.max_price) / running_max.max_price) * 100 
                ELSE 0 
              END
            ) as max_drawdown
          FROM stock_stats ss
          LEFT JOIN stock_prices sp ON ss.id = sp.stock_id
            AND sp.trading_date_local >= CURRENT_DATE - INTERVAL '1 day' * $3
          LEFT JOIN LATERAL (
            SELECT MAX(sp2.close_price) as max_price
            FROM stock_prices sp2
            WHERE sp2.stock_id = ss.id 
              AND sp2.trading_date_local <= sp.trading_date_local
              AND sp2.trading_date_local >= CURRENT_DATE - INTERVAL '1 day' * $3
          ) running_max ON true
          GROUP BY ss.id, ss.symbol
        )
        SELECT 
          ss.symbol,
          ss.name,
          ss.currency,
          ss.total_records,
          ss.latest_date,
          ROUND(ss.current_price::numeric, 2) as latest_price,
          -- Price Range (High - Low)
          ROUND((ss.highest_price - ss.lowest_price)::numeric, 2) as price_range,
          ROUND(ss.highest_price::numeric, 2) as highest_price,
          ROUND(ss.lowest_price::numeric, 2) as lowest_price,
          -- Total Return
          CASE 
            WHEN ss.first_price IS NOT NULL AND ss.first_price > 0 
            THEN ROUND((((ss.current_price - ss.first_price) / ss.first_price) * 100)::numeric, 2) 
            ELSE NULL 
          END as total_return,
          -- Max Drawdown
          COALESCE(ROUND(dc.max_drawdown::numeric, 2), 0) as max_drawdown
        FROM stock_stats ss
        LEFT JOIN daily_returns dr ON ss.id = dr.id
        LEFT JOIN drawdown_calc dc ON ss.id = dc.id
        ORDER BY ss.symbol;
      `;
      params = ['stock', true, daysBack];
    } else {
      // MAX timeframe - no date filtering
      query = `
        WITH stock_stats AS (
          SELECT 
            bi.id,
            bi.symbol,
            bi.name,
            bi.currency,
            COUNT(sp.id) as total_records,
            MAX(sp.trading_date_local) as latest_date,
            -- Current price (latest)
            (SELECT sp2.close_price 
             FROM stock_prices sp2 
             WHERE sp2.stock_id = bi.id 
             ORDER BY sp2.trading_date_local DESC 
             LIMIT 1) as current_price,
            -- First price for total return calculation (all time)
            (SELECT sp3.close_price 
             FROM stock_prices sp3 
             WHERE sp3.stock_id = bi.id 
             ORDER BY sp3.trading_date_local ASC 
             LIMIT 1) as first_price,
            -- Price range (high and low) - all time
            MAX(sp.high_price) as highest_price,
            MIN(sp.low_price) as lowest_price
          FROM base_instruments bi
          LEFT JOIN stock_prices sp ON bi.id = sp.stock_id
          WHERE bi.instrument_type = $1 AND bi.is_active = $2
          GROUP BY bi.id, bi.symbol, bi.name, bi.currency
        ),
        daily_returns AS (
          SELECT 
            ss.id,
            ss.symbol,
            AVG(
              CASE 
                WHEN prev_close.close_price IS NOT NULL AND prev_close.close_price > 0 
                THEN ((sp.close_price - prev_close.close_price) / prev_close.close_price) * 100 
                ELSE NULL 
              END
            ) as avg_daily_return
          FROM stock_stats ss
          LEFT JOIN stock_prices sp ON ss.id = sp.stock_id
          LEFT JOIN stock_prices prev_close ON ss.id = prev_close.stock_id 
            AND prev_close.trading_date_local = sp.trading_date_local - INTERVAL '1 day'
          GROUP BY ss.id, ss.symbol
        ),
        drawdown_calc AS (
          SELECT 
            ss.id,
            ss.symbol,
            -- Calculate running maximum and drawdown (all time)
            MIN(
              CASE 
                WHEN running_max.max_price > 0 
                THEN ((sp.close_price - running_max.max_price) / running_max.max_price) * 100 
                ELSE 0 
              END
            ) as max_drawdown
          FROM stock_stats ss
          LEFT JOIN stock_prices sp ON ss.id = sp.stock_id
          LEFT JOIN LATERAL (
            SELECT MAX(sp2.close_price) as max_price
            FROM stock_prices sp2
            WHERE sp2.stock_id = ss.id 
              AND sp2.trading_date_local <= sp.trading_date_local
          ) running_max ON true
          GROUP BY ss.id, ss.symbol
        )
        SELECT 
          ss.symbol,
          ss.name,
          ss.currency,
          ss.total_records,
          ss.latest_date,
          ROUND(ss.current_price::numeric, 2) as latest_price,
          -- Price Range (High - Low)
          ROUND((ss.highest_price - ss.lowest_price)::numeric, 2) as price_range,
          ROUND(ss.highest_price::numeric, 2) as highest_price,
          ROUND(ss.lowest_price::numeric, 2) as lowest_price,
          -- Total Return (all time)
          CASE 
            WHEN ss.first_price IS NOT NULL AND ss.first_price > 0 
            THEN ROUND((((ss.current_price - ss.first_price) / ss.first_price) * 100)::numeric, 2) 
            ELSE NULL 
          END as total_return,
          -- Max Drawdown (all time)
          COALESCE(ROUND(dc.max_drawdown::numeric, 2), 0) as max_drawdown
        FROM stock_stats ss
        LEFT JOIN daily_returns dr ON ss.id = dr.id
        LEFT JOIN drawdown_calc dc ON ss.id = dc.id
        ORDER BY ss.symbol;
      `;
      params = ['stock', true];
    }

    const result = await pool.query(query, params);
    
    const computationTime = Date.now() - startTime;
    console.log(`✅ Found ${result.rows.length} stocks with statistics (computed in ${computationTime}ms)`);
    console.log('First stock with stats:', result.rows[0]);
    
    // Cache the results
    await cacheManager.set(cacheKey, result.rows, timeframe);
    console.log(`📦 Cached results for ${timeframe} timeframe`);
    
    res.json(result.rows);
  } catch (error) {
    console.error('❌ Error fetching stocks:', error);
    res.status(500).json({ error: 'Failed to fetch stocks', details: error.message });
  }
});

// Get specific stock details with price history
app.get('/api/stocks/:symbol', async (req, res) => {
  const { symbol } = req.params;
  const { timeframe = '3M' } = req.query;
  
  console.log(`📈 Fetching details for stock: ${symbol}, timeframe: ${timeframe}`);
  
  // Check cache first (especially important for MAX timeframe)
  const cacheKey = cacheManager.getStockDetailKey(symbol, timeframe);
  const cachedData = await cacheManager.get(cacheKey);
  
  if (cachedData) {
    console.log(`⚡ Returning cached stock details for ${symbol} (${timeframe})`);
    return res.json(cachedData);
  }
  
  // Calculate date range based on timeframe
  let daysBack;
  let useTimeframeFilter = true;
  switch(timeframe) {
    case '1M': daysBack = 30; break;
    case '3M': daysBack = 90; break;
    case '6M': daysBack = 180; break;
    case '1Y': daysBack = 365; break;
    case 'MAX': 
      useTimeframeFilter = false; 
      daysBack = null;
      break;
    default: daysBack = 90;
  }
  
  try {
    await pool.query('SET search_path TO prod_stock_data');
    
    // Get stock info
    const stockInfo = await pool.query(`
      SELECT 
        bi.symbol,
        bi.name,
        bi.currency,
        COUNT(sp.id) as total_records,
        MAX(sp.trading_date_local) as latest_date,
        (SELECT sp2.close_price 
         FROM stock_prices sp2 
         WHERE sp2.stock_id = bi.id 
         ORDER BY sp2.trading_date_local DESC 
         LIMIT 1) as latest_price
      FROM base_instruments bi
      LEFT JOIN stock_prices sp ON bi.id = sp.stock_id
      WHERE bi.symbol = $1 AND bi.instrument_type = $2
      GROUP BY bi.id, bi.symbol, bi.name, bi.currency;
    `, [symbol, 'stock']);
    
    if (stockInfo.rows.length === 0) {
      return res.status(404).json({ error: 'Stock not found' });
    }
    
    // Get price history with conditional timeframe filtering
    let priceHistoryQuery;
    let priceHistoryParams;
    
    if (useTimeframeFilter) {
      // Use timeframe filter for 1M, 3M, 6M, 1Y
      priceHistoryQuery = `
        SELECT 
          sp.trading_date_local as date,
          sp.open_price as open,
          sp.high_price as high,
          sp.low_price as low,
          sp.close_price as close,
          sp.volume
        FROM stock_prices sp
        JOIN base_instruments bi ON sp.stock_id = bi.id
        WHERE bi.symbol = $1 
          AND sp.trading_date_local >= CURRENT_DATE - INTERVAL '1 day' * $2
        ORDER BY sp.trading_date_local ASC;
      `;
      priceHistoryParams = [symbol, daysBack];
    } else {
      // MAX timeframe - get all historical data
      priceHistoryQuery = `
        SELECT 
          sp.trading_date_local as date,
          sp.open_price as open,
          sp.high_price as high,
          sp.low_price as low,
          sp.close_price as close,
          sp.volume
        FROM stock_prices sp
        JOIN base_instruments bi ON sp.stock_id = bi.id
        WHERE bi.symbol = $1
        ORDER BY sp.trading_date_local ASC;
      `;
      priceHistoryParams = [symbol];
    }
    
    const priceHistory = await pool.query(priceHistoryQuery, priceHistoryParams);
    
    const response = {
      ...stockInfo.rows[0],
      price_history: priceHistory.rows
    };
    
    console.log(`✅ Found ${response.total_records} total records, ${priceHistory.rows.length} in timeframe`);
    
    // Cache the results (especially important for MAX timeframe)
    await cacheManager.set(cacheKey, response, timeframe);
    console.log(`📦 Cached stock details for ${symbol} (${timeframe})`);
    
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching stock details:', error);
    res.status(500).json({ error: 'Failed to fetch stock details', details: error.message });
  }
});

// Get ML predictions for a stock
app.get('/api/predictions/:symbol', async (req, res) => {
  const { symbol } = req.params;
  const { limit = 30 } = req.query;
  
  console.log(`🔮 Fetching ML predictions for stock: ${symbol}`);
  
  try {
    await pool.query('SET search_path TO prod_stock_data');
    
    const result = await pool.query(`
      SELECT 
        mp.prediction_date,
        mp.target_date,
        mp.predicted_class,
        mp.prediction_probability,
        mp.trading_signal,
        mp.actual_class
      FROM ml_predictions mp
      JOIN base_instruments bi ON mp.instrument_id = bi.id
      WHERE bi.symbol = $1
      ORDER BY mp.prediction_date DESC
      LIMIT $2;
    `, [symbol, parseInt(limit)]);
    
    console.log(`✅ Found ${result.rows.length} predictions for ${symbol}`);
    res.json(result.rows);
  } catch (error) {
    console.error('❌ Error fetching predictions:', error);
    res.status(500).json({ error: 'Failed to fetch predictions', details: error.message });
  }
});

// Get enhanced analytics data for a stock
app.get('/api/stocks/:symbol/analytics', async (req, res) => {
  const { symbol } = req.params;
  const { timeframe = '1Y' } = req.query;
  
  console.log(`📊 Fetching analytics for stock: ${symbol}, timeframe: ${timeframe}`);
  
  // Check cache first
  const cacheKey = cacheManager.getStockStatsKey(symbol, timeframe);
  const cachedData = await cacheManager.get(cacheKey);
  
  if (cachedData) {
    console.log(`⚡ Returning cached analytics for ${symbol} (${timeframe})`);
    return res.json(cachedData);
  }
  
  // Calculate date range based on timeframe
  let daysBack;
  switch(timeframe) {
    case '1M': daysBack = 30; break;
    case '3M': daysBack = 90; break;
    case '6M': daysBack = 180; break;
    case '1Y': daysBack = 365; break;
    case '2Y': daysBack = 730; break;
    case 'ALL': daysBack = 3650; break; // ~10 years
    case 'MAX': daysBack = 3650; break; // All available data
    default: daysBack = 365;
  }
  
  const startTime = Date.now();
  console.log(`🔍 Cache MISS - Computing analytics for ${symbol} (${timeframe})...`);
  
  try {
    await pool.query('SET search_path TO prod_stock_data');
    
    // Enhanced query with moving averages and technical indicators
    const analyticsResult = await pool.query(`
      WITH price_data AS (
        SELECT 
          sp.trading_date_local as date,
          sp.open_price as open,
          sp.high_price as high,
          sp.low_price as low,
          sp.close_price as close,
          sp.volume,
          LAG(sp.close_price) OVER (ORDER BY sp.trading_date_local) as prev_close
        FROM stock_prices sp
        JOIN base_instruments bi ON sp.stock_id = bi.id
        WHERE bi.symbol = $1 
          AND sp.trading_date_local >= CURRENT_DATE - INTERVAL '1 day' * $2
        ORDER BY sp.trading_date_local ASC
      ),
      returns_data AS (
        SELECT 
          *,
          -- Daily return calculation
          CASE 
            WHEN prev_close IS NOT NULL AND prev_close > 0 
            THEN ((close - prev_close) / prev_close) * 100 
            ELSE NULL 
          END as daily_return
        FROM price_data
      ),
      enhanced_data AS (
        SELECT 
          *,
          -- Moving averages
          AVG(close) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as ma_20,
          AVG(close) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) as ma_50,
          AVG(volume) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as volume_ma_20,
          -- 20-day rolling volatility (standard deviation of daily returns)
          STDDEV(daily_return) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as volatility_20d
        FROM returns_data
      )
      SELECT 
        date,
        open,
        high,
        low,
        close,
        volume,
        daily_return,
        ROUND(ma_20::numeric, 2) as ma_20,
        ROUND(ma_50::numeric, 2) as ma_50,
        ROUND(volume_ma_20::numeric, 0) as volume_ma_20,
        ROUND(volatility_20d::numeric, 3) as volatility_20d
      FROM enhanced_data
      ORDER BY date;
    `, [symbol, daysBack]);
    
    const computationTime = Date.now() - startTime;
    const responseData = {
      symbol: symbol,
      timeframe: timeframe,
      data: analyticsResult.rows
    };
    
    console.log(`✅ Analytics data for ${symbol}: ${analyticsResult.rows.length} records (computed in ${computationTime}ms)`);
    
    // Cache the results
    await cacheManager.set(cacheKey, responseData, timeframe);
    console.log(`📦 Cached analytics for ${symbol} (${timeframe})`);
    
    res.json(responseData);
    
  } catch (error) {
    console.error('❌ Error fetching analytics:', error);
    res.status(500).json({ error: 'Failed to fetch analytics', details: error.message });
  }
});

// Get monthly statistics for a stock
app.get('/api/stocks/:symbol/monthly-stats', async (req, res) => {
  const { symbol } = req.params;
  const { years = 2 } = req.query;
  
  console.log(`📅 Fetching monthly stats for stock: ${symbol}, years: ${years}`);
  
  try {
    await pool.query('SET search_path TO prod_stock_data');
    
    const monthlyResult = await pool.query(`
      WITH daily_data AS (
        SELECT 
          sp.trading_date_local as date,
          sp.close_price as close,
          sp.volume,
          LAG(sp.close_price) OVER (ORDER BY sp.trading_date_local) as prev_close,
          DATE_TRUNC('month', sp.trading_date_local) as month
        FROM stock_prices sp
        JOIN base_instruments bi ON sp.stock_id = bi.id
        WHERE bi.symbol = $1 
          AND sp.trading_date_local >= CURRENT_DATE - INTERVAL '1 year' * $2
        ORDER BY sp.trading_date_local ASC
      ),
      daily_returns AS (
        SELECT 
          date,
          close,
          volume,
          month,
          CASE 
            WHEN prev_close IS NOT NULL AND prev_close > 0 
            THEN ((close - prev_close) / prev_close) * 100 
            ELSE NULL 
          END as daily_return
        FROM daily_data
      )
      SELECT 
        month,
        COUNT(*) as trading_days,
        ROUND((ARRAY_AGG(close ORDER BY date))[1]::numeric, 2) as open_price,
        ROUND((ARRAY_AGG(close ORDER BY date DESC))[1]::numeric, 2) as close_price,
        ROUND(MAX(close)::numeric, 2) as high_price,
        ROUND(MIN(close)::numeric, 2) as low_price,
        ROUND(AVG(close)::numeric, 2) as avg_price,
        ROUND(AVG(volume)::numeric, 0) as avg_volume,
        SUM(volume) as total_volume,
        ROUND(AVG(daily_return)::numeric, 3) as avg_daily_return,
        ROUND(STDDEV(daily_return)::numeric, 3) as daily_return_volatility,
        ROUND(MIN(daily_return)::numeric, 2) as min_daily_return,
        ROUND(MAX(daily_return)::numeric, 2) as max_daily_return,
        ROUND((((ARRAY_AGG(close ORDER BY date DESC))[1] - (ARRAY_AGG(close ORDER BY date))[1]) / (ARRAY_AGG(close ORDER BY date))[1] * 100)::numeric, 2) as monthly_return
      FROM daily_returns
      GROUP BY month
      ORDER BY month;
    `, [symbol, parseInt(years)]);
    
    console.log(`✅ Monthly stats for ${symbol}: ${monthlyResult.rows.length} months`);
    res.json({
      symbol: symbol,
      years: parseInt(years),
      monthly_stats: monthlyResult.rows
    });
    
  } catch (error) {
    console.error('❌ Error fetching monthly stats:', error);
    res.status(500).json({ error: 'Failed to fetch monthly stats', details: error.message });
  }
});

// Get statistical analysis data for a stock
app.get('/api/stocks/:symbol/statistics', async (req, res) => {
  const { symbol } = req.params;
  
  console.log(`📈 Fetching statistics for stock: ${symbol}`);
  
  try {
    await pool.query('SET search_path TO prod_stock_data');
    
    // Statistical analysis query
    const statsResult = await pool.query(`
      WITH daily_data AS (
        SELECT 
          sp.trading_date_local as date,
          sp.close_price as close,
          sp.volume,
          LAG(sp.close_price) OVER (ORDER BY sp.trading_date_local) as prev_close
        FROM stock_prices sp
        JOIN base_instruments bi ON sp.stock_id = bi.id
        WHERE bi.symbol = $1
        ORDER BY sp.trading_date_local ASC
      ),
      returns_data AS (
        SELECT 
          *,
          CASE 
            WHEN prev_close IS NOT NULL AND prev_close > 0 
            THEN ((close - prev_close) / prev_close) * 100 
            ELSE NULL 
          END as daily_return
        FROM daily_data
        WHERE prev_close IS NOT NULL
      ),
      distribution_buckets AS (
        SELECT 
          WIDTH_BUCKET(daily_return, -20, 20, 40) as bucket,
          COUNT(*) as frequency,
          AVG(daily_return) as avg_return_in_bucket
        FROM returns_data
        WHERE daily_return BETWEEN -20 AND 20
        GROUP BY WIDTH_BUCKET(daily_return, -20, 20, 40)
        ORDER BY bucket
      ),
      correlation_data AS (
        SELECT 
          close,
          volume,
          daily_return
        FROM returns_data
        ORDER BY date DESC
        LIMIT 1000  -- Last 1000 trading days for correlation
      )
      SELECT 
        -- Basic statistics
        (SELECT COUNT(*) FROM returns_data) as total_days,
        (SELECT AVG(daily_return) FROM returns_data) as avg_daily_return,
        (SELECT STDDEV(daily_return) FROM returns_data) as return_volatility,
        (SELECT MIN(daily_return) FROM returns_data) as min_daily_return,
        (SELECT MAX(daily_return) FROM returns_data) as max_daily_return,
        (SELECT PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY daily_return) FROM returns_data) as return_5th_percentile,
        (SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY daily_return) FROM returns_data) as return_95th_percentile,
        
        -- Price-Volume correlation
        (SELECT CORR(close, volume) FROM correlation_data) as price_volume_correlation,
        
        -- Current vs historical metrics
        (SELECT close FROM returns_data ORDER BY date DESC LIMIT 1) as current_price,
        (SELECT close FROM returns_data ORDER BY date ASC LIMIT 1) as first_price,
        (SELECT MAX(close) FROM returns_data) as highest_price,
        (SELECT MIN(close) FROM returns_data) as lowest_price,
        
        -- Distribution data for histogram
        (SELECT json_agg(json_build_object('bucket', bucket, 'frequency', frequency, 'return_range', avg_return_in_bucket) ORDER BY bucket) 
         FROM distribution_buckets) as return_distribution;
    `, [symbol]);
    
    const correlationData = await pool.query(`
      WITH daily_data AS (
        SELECT 
          sp.close_price as close,
          sp.volume,
          LAG(sp.close_price) OVER (ORDER BY sp.trading_date_local) as prev_close
        FROM stock_prices sp
        JOIN base_instruments bi ON sp.stock_id = bi.id
        WHERE bi.symbol = $1
        ORDER BY sp.trading_date_local DESC
        LIMIT 500  -- Last 500 days for scatter plot
      )
      SELECT 
        close,
        volume,
        CASE 
          WHEN prev_close IS NOT NULL AND prev_close > 0 
          THEN ((close - prev_close) / prev_close) * 100 
          ELSE NULL 
        END as daily_return
      FROM daily_data
      WHERE prev_close IS NOT NULL
      ORDER BY close;
    `, [symbol]);
    
    const stats = statsResult.rows[0];
    
    // Calculate additional performance metrics
    const totalReturn = ((stats.current_price - stats.first_price) / stats.first_price) * 100;
    const annualizedReturn = Math.pow((stats.current_price / stats.first_price), (365.25 / stats.total_days)) - 1;
    const annualizedVolatility = stats.return_volatility * Math.sqrt(252); // Assuming 252 trading days per year
    const sharpeRatio = (annualizedReturn - 0.04) / (annualizedVolatility / 100); // Assuming 4% risk-free rate
    const maxDrawdown = ((stats.lowest_price - stats.highest_price) / stats.highest_price) * 100;
    
    console.log(`✅ Statistics for ${symbol}: ${stats.total_days} days of data`);
    res.json({
      symbol: symbol,
      basic_stats: {
        total_days: stats.total_days,
        avg_daily_return: parseFloat(stats.avg_daily_return).toFixed(3),
        return_volatility: parseFloat(stats.return_volatility).toFixed(3),
        min_daily_return: parseFloat(stats.min_daily_return).toFixed(2),
        max_daily_return: parseFloat(stats.max_daily_return).toFixed(2),
        return_5th_percentile: parseFloat(stats.return_5th_percentile).toFixed(2),
        return_95th_percentile: parseFloat(stats.return_95th_percentile).toFixed(2)
      },
      price_stats: {
        current_price: parseFloat(stats.current_price).toFixed(2),
        first_price: parseFloat(stats.first_price).toFixed(2),
        highest_price: parseFloat(stats.highest_price).toFixed(2),
        lowest_price: parseFloat(stats.lowest_price).toFixed(2),
        total_return: totalReturn.toFixed(2),
        max_drawdown: maxDrawdown.toFixed(2)
      },
      performance_metrics: {
        annualized_return: (annualizedReturn * 100).toFixed(2),
        annualized_volatility: annualizedVolatility.toFixed(2),
        sharpe_ratio: sharpeRatio.toFixed(2),
        price_volume_correlation: parseFloat(stats.price_volume_correlation).toFixed(4)
      },
      return_distribution: stats.return_distribution,
      correlation_data: correlationData.rows
    });
    
  } catch (error) {
    console.error('❌ Error fetching statistics:', error);
    res.status(500).json({ error: 'Failed to fetch statistics', details: error.message });
  }
});

// Cache status endpoint
app.get('/api/cache/status', async (req, res) => {
  try {
    const stats = await cacheManager.getStats();
    res.json({
      status: 'OK',
      cache: stats,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ Error fetching cache status:', error);
    res.status(500).json({ error: 'Failed to fetch cache status', details: error.message });
  }
});

// Cache invalidation endpoints
app.delete('/api/cache/:timeframe', async (req, res) => {
  try {
    const { timeframe } = req.params;
    await cacheManager.invalidate(timeframe);
    res.json({
      status: 'OK',
      message: `Cache invalidated for timeframe: ${timeframe}`,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ Error invalidating cache:', error);
    res.status(500).json({ error: 'Failed to invalidate cache', details: error.message });
  }
});

app.delete('/api/cache', async (req, res) => {
  try {
    await cacheManager.invalidate('ALL');
    res.json({
      status: 'OK',
      message: 'Cache invalidated for all timeframes',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ Error invalidating cache:', error);
    res.status(500).json({ error: 'Failed to invalidate cache', details: error.message });
  }
});

// ETL webhook for cache invalidation on new daily data
app.post('/api/etl/data-loaded', async (req, res) => {
  try {
    const { symbols, trading_date, records_count } = req.body;
    
    console.log(`📈 ETL webhook triggered - New data loaded for ${symbols?.length || 'unknown'} symbols on ${trading_date}`);
    console.log(`📊 Records processed: ${records_count || 'unknown'}`);
    
    // Invalidate cache for MAX timeframe since it contains all historical data
    // and needs to include the new daily data
    await cacheManager.invalidate('MAX');
    console.log('🗑️ Invalidated MAX timeframe cache due to new daily data');
    
    // Also invalidate recent timeframes that might include the new trading day
    const timeframesToInvalidate = ['1M', '3M', '6M', '1Y'];
    for (const timeframe of timeframesToInvalidate) {
      await cacheManager.invalidate(timeframe);
      console.log(`🗑️ Invalidated ${timeframe} timeframe cache`);
    }
    
    res.json({
      status: 'OK',
      message: `Cache invalidated for new data on ${trading_date}`,
      symbols_processed: symbols?.length || 0,
      records_count: records_count || 0,
      timeframes_invalidated: ['MAX', ...timeframesToInvalidate],
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ Error processing ETL webhook:', error);
    res.status(500).json({ 
      error: 'Failed to process ETL webhook', 
      details: error.message 
    });
  }
});

// Get ML analytics for a specific stock
app.get('/api/stocks/:symbol/ml-analytics', async (req, res) => {
  const { symbol } = req.params;
  console.log(`🤖 Fetching ML analytics for ${symbol}...`);
  
  // Check cache first
  const cacheKey = `ml_analytics:${symbol}`;
  const cachedData = await cacheManager.get(cacheKey);
  
  if (cachedData) {
    console.log(`⚡ Returning cached ML analytics for ${symbol}`);
    return res.json(cachedData);
  }
  
  try {
    await pool.query('SET search_path TO prod_stock_data');
    
    // Get instrument ID for symbol
    const instrumentResult = await pool.query(`
      SELECT id FROM base_instruments WHERE symbol = $1
    `, [symbol.toUpperCase()]);
    
    if (instrumentResult.rows.length === 0) {
      return res.status(404).json({ error: `Stock ${symbol} not found` });
    }
    
    const instrumentId = instrumentResult.rows[0].id;
    
    // Get model information
    const modelResult = await pool.query(`
      SELECT 
        model_version,
        status,
        test_roc_auc,
        test_accuracy,
        training_records,
        validation_records,
        test_records,
        feature_count,
        training_start_date,
        training_end_date,
        hyperparameters,
        feature_importance,
        trained_at
      FROM ml_models 
      WHERE instrument_id = $1 AND status = 'active'
      ORDER BY trained_at DESC
      LIMIT 1
    `, [instrumentId]);
    
    if (modelResult.rows.length === 0) {
      return res.status(404).json({ error: `No ML model found for ${symbol}` });
    }
    
    const modelInfo = modelResult.rows[0];
    
    // Get confusion matrix data (predictions with actual outcomes)
    const confusionResult = await pool.query(`
      SELECT 
        predicted_class::int as predicted_class,
        actual_class::int as actual_class,
        COUNT(*) as count 
      FROM ml_predictions 
      WHERE instrument_id = $1 AND actual_class IS NOT NULL
      GROUP BY predicted_class, actual_class
      ORDER BY predicted_class, actual_class
    `, [instrumentId]);
    
    // Build confusion matrix
    const confusionMatrix = [[0, 0], [0, 0]];
    confusionResult.rows.forEach(row => {
      confusionMatrix[row.actual_class][row.predicted_class] = parseInt(row.count);
    });
    
    // Get ROC curve data
    const rocResult = await pool.query(`
      SELECT 
        prediction_probability,
        actual_class::int as actual_class
      FROM ml_predictions 
      WHERE instrument_id = $1 AND actual_class IS NOT NULL
      ORDER BY prediction_probability DESC
      LIMIT 1000
    `, [instrumentId]);
    
    // Calculate ROC curve points
    const rocData = calculateROCCurve(rocResult.rows);
    
    // Get predictions summary
    const predSummaryResult = await pool.query(`
      SELECT 
        COUNT(*) as total_predictions,
        COUNT(CASE WHEN predicted_class = true THEN 1 END) as positive_predictions,
        COUNT(CASE WHEN predicted_class = false THEN 1 END) as negative_predictions,
        COUNT(CASE WHEN actual_class IS NOT NULL AND predicted_class = actual_class THEN 1 END)::float / 
          NULLIF(COUNT(CASE WHEN actual_class IS NOT NULL THEN 1 END), 0) as accuracy_rate
      FROM ml_predictions 
      WHERE instrument_id = $1
    `, [instrumentId]);
    
    // Get latest predictions
    const latestPredsResult = await pool.query(`
      SELECT 
        prediction_date,
        target_date,
        predicted_class,
        prediction_probability,
        actual_class,
        trading_signal
      FROM ml_predictions 
      WHERE instrument_id = $1
      ORDER BY prediction_date DESC
      LIMIT 10
    `, [instrumentId]);
    
    // Get backtest results
    const backtestResult = await pool.query(`
      SELECT 
        total_return,
        sharpe_ratio,
        win_rate,
        total_trades,
        max_drawdown,
        annualized_return
      FROM ml_backtest_results 
      WHERE instrument_id = $1
      ORDER BY backtest_end_date DESC
      LIMIT 1
    `, [instrumentId]);
    
    // Parse feature importance
    let featureImportance = [];
    try {
      if (modelInfo.feature_importance) {
        const importance = JSON.parse(modelInfo.feature_importance);
        featureImportance = Object.entries(importance)
          .map(([feature_name, importance_value]) => ({
            feature_name,
            importance: importance_value
          }))
          .sort((a, b) => b.importance - a.importance)
          .slice(0, 15);
      }
    } catch (e) {
      console.warn(`⚠️ Could not parse feature importance for ${symbol}:`, e.message);
    }
    
    const response = {
      symbol,
      model_info: {
        model_version: modelInfo.model_version,
        status: modelInfo.status,
        test_roc_auc: parseFloat(modelInfo.test_roc_auc || 0),
        test_accuracy: parseFloat(modelInfo.test_accuracy || 0),
        training_records: parseInt(modelInfo.training_records || 0),
        validation_records: parseInt(modelInfo.validation_records || 0),
        test_records: parseInt(modelInfo.test_records || 0),
        feature_count: parseInt(modelInfo.feature_count || 0),
        training_start_date: modelInfo.training_start_date,
        training_end_date: modelInfo.training_end_date,
        trained_at: modelInfo.trained_at
      },
      performance_metrics: {
        confusion_matrix: confusionMatrix,
        roc_curve: rocData
      },
      predictions_summary: {
        total_predictions: parseInt(predSummaryResult.rows[0].total_predictions),
        positive_predictions: parseInt(predSummaryResult.rows[0].positive_predictions),
        negative_predictions: parseInt(predSummaryResult.rows[0].negative_predictions),
        accuracy_rate: parseFloat(predSummaryResult.rows[0].accuracy_rate || 0),
        latest_predictions: latestPredsResult.rows.map(pred => ({
          prediction_date: pred.prediction_date,
          target_date: pred.target_date,
          predicted_class: pred.predicted_class,
          prediction_probability: parseFloat(pred.prediction_probability),
          actual_class: pred.actual_class,
          trading_signal: pred.trading_signal
        }))
      },
      backtest_results: backtestResult.rows[0] ? {
        total_return: parseFloat(backtestResult.rows[0].total_return || 0),
        sharpe_ratio: parseFloat(backtestResult.rows[0].sharpe_ratio || 0),
        win_rate: parseFloat(backtestResult.rows[0].win_rate || 0),
        total_trades: parseInt(backtestResult.rows[0].total_trades || 0),
        max_drawdown: parseFloat(backtestResult.rows[0].max_drawdown || 0),
        annualized_return: parseFloat(backtestResult.rows[0].annualized_return || 0)
      } : null,
      feature_importance: featureImportance
    };
    
    // Cache for 24 hours (ML data doesn't change frequently)
    await cacheManager.set(cacheKey, response, 86400);
    
    console.log(`✅ ML analytics for ${symbol} compiled successfully`);
    res.json(response);
    
  } catch (error) {
    console.error(`❌ Error fetching ML analytics for ${symbol}:`, error);
    res.status(500).json({ 
      error: 'Failed to fetch ML analytics', 
      details: error.message 
    });
  }
});

// Helper function to calculate ROC curve points
function calculateROCCurve(predictions) {
  if (predictions.length === 0) return { fpr: [0, 1], tpr: [0, 1] };
  
  const sorted = predictions.sort((a, b) => b.prediction_probability - a.prediction_probability);
  const positives = sorted.filter(p => p.actual_class === 1).length;
  const negatives = sorted.filter(p => p.actual_class === 0).length;
  
  if (positives === 0 || negatives === 0) return { fpr: [0, 1], tpr: [0, 1] };
  
  const fpr = [0];
  const tpr = [0];
  let tp = 0, fp = 0;
  
  for (let i = 0; i < sorted.length; i++) {
    if (sorted[i].actual_class === 1) tp++;
    else fp++;
    
    // Add point every 10% of data to avoid too many points
    if (i % Math.max(1, Math.floor(sorted.length / 20)) === 0 || i === sorted.length - 1) {
      fpr.push(fp / negatives);
      tpr.push(tp / positives);
    }
  }
  
  return { fpr, tpr };
}

// Get model performance
app.get('/api/models', async (req, res) => {
  console.log('🤖 Fetching ML models performance...');
  
  try {
    await pool.query('SET search_path TO prod_stock_data');
    
    const result = await pool.query(`
      SELECT 
        bi.symbol,
        mm.model_version,
        mm.test_roc_auc,
        mm.test_accuracy,
        mm.hyperparameters,
        mm.trained_at
      FROM ml_models mm
      JOIN base_instruments bi ON mm.instrument_id = bi.id
      WHERE mm.status = $1
      ORDER BY mm.test_roc_auc DESC;
    `, ['active']);
    
    console.log(`✅ Found ${result.rows.length} active ML models`);
    res.json(result.rows);
  } catch (error) {
    console.error('❌ Error fetching models:', error);
    res.status(500).json({ error: 'Failed to fetch models', details: error.message });
  }
});

// Initialize cache and start server
async function startServer() {
  try {
    // Initialize Redis cache
    await cacheManager.connect();
    
    app.listen(port, () => {
      console.log(`🚀 Backend server running on http://localhost:${port}`);
      console.log(`📊 Connected to database: ${process.env.DB_NAME || 'stock_data'}`);
      console.log(`📦 Redis cache: ${cacheManager.isConnected ? 'Connected' : 'Unavailable (graceful degradation)'}`);
      console.log(`🗂️  Using schema: prod_stock_data`);
    });
  } catch (error) {
    console.error('❌ Server startup error:', error);
    // Start server anyway with graceful degradation
    app.listen(port, () => {
      console.log(`🚀 Backend server running on http://localhost:${port} (without cache)`);
      console.log(`📊 Connected to database: ${process.env.DB_NAME || 'stock_data'}`);
      console.log(`🗂️  Using schema: prod_stock_data`);
    });
  }
}

startServer();
