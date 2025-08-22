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
