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

// Get all stocks
app.get('/api/stocks', async (req, res) => {
  try {
    const result = await pool.query(`
      SET search_path TO prod_stock_data;
      SELECT 
        bi.symbol,
        bi.name,
        bi.currency,
        COUNT(sp.id) as total_records,
        MAX(sp.trading_date_local) as latest_date,
        sp.close_price as latest_price
      FROM base_instruments bi
      LEFT JOIN stock_prices sp ON bi.id = sp.stock_id
      WHERE bi.instrument_type = 'stock'
      GROUP BY bi.id, bi.symbol, bi.name, bi.currency, sp.close_price
      ORDER BY bi.symbol;
    `);
    
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching stocks:', error);
    res.status(500).json({ error: 'Failed to fetch stocks' });
  }
});

// Get specific stock details
app.get('/api/stocks/:symbol', async (req, res) => {
  const { symbol } = req.params;
  
  try {
    const result = await pool.query(`
      SET search_path TO prod_stock_data;
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
      ORDER BY sp.trading_date_local DESC
      LIMIT 100;
    `, [symbol]);
    
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching stock details:', error);
    res.status(500).json({ error: 'Failed to fetch stock details' });
  }
});

// Get ML predictions for a stock
app.get('/api/predictions/:symbol', async (req, res) => {
  const { symbol } = req.params;
  
  try {
    const result = await pool.query(`
      SET search_path TO prod_stock_data;
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
      LIMIT 30;
    `, [symbol]);
    
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching predictions:', error);
    res.status(500).json({ error: 'Failed to fetch predictions' });
  }
});

// Get model performance
app.get('/api/models', async (req, res) => {
  try {
    const result = await pool.query(`
      SET search_path TO prod_stock_data;
      SELECT 
        bi.symbol,
        mm.model_version,
        mm.test_roc_auc,
        mm.test_accuracy,
        mm.hyperparameters,
        mm.trained_at
      FROM ml_models mm
      JOIN base_instruments bi ON mm.instrument_id = bi.id
      WHERE mm.status = 'active'
      ORDER BY mm.test_roc_auc DESC;
    `);
    
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching models:', error);
    res.status(500).json({ error: 'Failed to fetch models' });
  }
});

app.listen(port, () => {
  console.log(`🚀 Backend server running on http://localhost:${port}`);
  console.log(`📊 Connected to database: ${process.env.DB_NAME || 'stock_data'}`);
  console.log(`🗂️  Using schema: prod_stock_data`);
});