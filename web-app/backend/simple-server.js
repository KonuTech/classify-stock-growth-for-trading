const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const app = express();
const port = 3001;

// Database connection
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'stock_data',
  user: 'postgres',
  password: 'postgres',
});

app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Simple database test
app.get('/test-db', async (req, res) => {
  try {
    await pool.query('SET search_path TO prod_stock_data');
    const result = await pool.query('SELECT COUNT(*) as count FROM base_instruments WHERE instrument_type = $1', ['stock']);
    res.json({ 
      status: 'OK', 
      stockCount: result.rows[0].count 
    });
  } catch (error) {
    console.error('Database error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get stocks with all required fields
app.get('/api/stocks', async (req, res) => {
  console.log('📊 Fetching stocks...');
  try {
    await pool.query('SET search_path TO prod_stock_data');
    
    const result = await pool.query(`
      SELECT 
        bi.symbol,
        bi.name,
        bi.currency,
        COALESCE(COUNT(sp.id), 0) as total_records,
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
      ORDER BY bi.symbol
    `, ['stock', true]);
    
    console.log(`✅ Found ${result.rows.length} stocks`);
    console.log('Sample:', result.rows[0]);
    res.json(result.rows);
  } catch (error) {
    console.error('❌ Error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`🚀 Simple server running on http://localhost:${port}`);
});