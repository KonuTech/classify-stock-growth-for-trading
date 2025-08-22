const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { Pool } = require('pg');

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

// Get all stocks
app.get('/api/stocks', async (req, res) => {
  console.log('📊 Fetching stocks from prod_stock_data...');
  try {
    // Test basic connection first
    const testResult = await pool.query('SELECT 1 as test');
    console.log('✅ Database connection working');
    
    await pool.query('SET search_path TO prod_stock_data');
    console.log('✅ Search path set to prod_stock_data');
    
    // Get all stocks with their latest price and record count
    const result = await pool.query(`
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
      WHERE bi.instrument_type = $1 AND bi.is_active = $2
      GROUP BY bi.id, bi.symbol, bi.name, bi.currency
      ORDER BY bi.symbol;
    `, ['stock', true]);
    
    console.log(`✅ Found ${result.rows.length} stocks`);
    console.log('First few stocks:', result.rows.slice(0, 3));
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
  
  // Calculate date range based on timeframe
  let daysBack;
  switch(timeframe) {
    case '1M': daysBack = 30; break;
    case '3M': daysBack = 90; break;
    case '6M': daysBack = 180; break;
    case '1Y': daysBack = 365; break;
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
    
    // Get price history with parameterized query
    const priceHistory = await pool.query(`
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
    `, [symbol, daysBack]);
    
    const response = {
      ...stockInfo.rows[0],
      price_history: priceHistory.rows
    };
    
    console.log(`✅ Found ${response.total_records} total records, ${priceHistory.rows.length} in timeframe`);
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
  
  // Calculate date range based on timeframe
  let daysBack;
  switch(timeframe) {
    case '1M': daysBack = 30; break;
    case '3M': daysBack = 90; break;
    case '6M': daysBack = 180; break;
    case '1Y': daysBack = 365; break;
    case '2Y': daysBack = 730; break;
    case 'ALL': daysBack = 3650; break; // ~10 years
    default: daysBack = 365;
  }
  
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
    
    console.log(`✅ Analytics data for ${symbol}: ${analyticsResult.rows.length} records`);
    res.json({
      symbol: symbol,
      timeframe: timeframe,
      data: analyticsResult.rows
    });
    
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

app.listen(port, () => {
  console.log(`🚀 Backend server running on http://localhost:${port}`);
  console.log(`📊 Connected to database: ${process.env.DB_NAME || 'stock_data'}`);
  console.log(`🗂️  Using schema: prod_stock_data`);
});
