# ML Pipeline Integration Plan - UPDATED
## Dynamic Multi-Instrument ML Training with Airflow DAGs (7-Day Targets)

**Updated**: 2025-08-20  
**Status**: Ready for Implementation  
**Target System**: 7-Day Growth Prediction (Refactored from 30-Day)  
**Database**: 10 stocks + 4 indices in test_stock_data

---

## 🎯 **CRITICAL UPDATE: 7-Day Target System**

### **Refactoring Completed** ✅
- **Feature Engineering**: Default `target_days = 7` 
- **Backtesting**: 7-day holding periods
- **Column Names**: `growth_future_7d` (consistent naming)
- **Performance**: **7-day targets produce better models** than 30-day
- **Benefits**: More predictable patterns, higher signal-to-noise ratio, weekly market cycles

### **Actual DataFrame Analysis Results** ✅ VERIFIED

#### **Feature Engineering DataFrame (DOCUMENTED)**
**Source**: `step02_feature_engineering_output_xtb.md`
- **Shape**: 2,255 rows × 193 columns (XTB stock)
- **Memory**: 3.43 MB per stock
- **Features Created**: 183 engineered features
- **Target Variable**: `target` (binary) + `growth_future_7d` (7-day growth ratio)
- **Key Feature Categories**:
  - **Price Features** (9): close_price, open_price, high_price, low_price, volume
  - **Technical Indicators** (33): rsi_14, macd_line, macd_signal, bollinger_upper, bollinger_lower, stoch_k, williams_r, atr_14, adx_14, cci_20
  - **Volume Features** (8): volume, volume_sma_5, volume_sma_10, volume_ratio_5d  
  - **Growth Features** (9): growth_1d, growth_3d, growth_7d, returns_1d, returns_3d
  - **Target Variables** (2): `target` (binary 7-day growth), `growth_future_7d` (raw ratio)

#### **Storage Estimates (Updated for 7-Day System)**
**Per Stock Daily Training**:
- **Feature Data**: 3.43 MB × 10 stocks = 34.3 MB daily
- **Model Results**: 1 KB × 10 stocks = 10 KB daily  
- **Predictions**: 20 KB × 10 stocks = 200 KB daily (7-day predictions)
- **Backtest Results**: 5 KB × 10 stocks = 50 KB daily
- **Total Daily Storage**: ~35 MB per day for all 10 stocks

---

## Phase 1: Database Schema Extension for ML Artifacts (7-Day System)

### **Updated ML Tables for 7-Day Targets**

#### 1. ML Models Table (Updated)
```sql
CREATE TABLE IF NOT EXISTS ml_models (
    id BIGSERIAL PRIMARY KEY,
    instrument_id INTEGER NOT NULL REFERENCES base_instruments(id),
    model_version VARCHAR(50) NOT NULL,  -- v2.0.0 (7-day system)
    model_type VARCHAR(50) NOT NULL DEFAULT 'xgboost_classifier',
    model_name VARCHAR(100) NOT NULL,    -- XTB_growth_7d_classifier_v2.0.0
    
    -- Model Configuration (7-Day System)
    hyperparameters JSONB NOT NULL,      -- XGBoost hyperparameters
    feature_count INTEGER NOT NULL,      -- ~183 features per stock
    target_variable VARCHAR(50) NOT NULL DEFAULT 'growth_7d',  -- 7-day targets
    target_horizon_days INTEGER NOT NULL DEFAULT 7,            -- 7-day prediction horizon
    
    -- Performance Metrics  
    cv_score DECIMAL(8,6),
    test_accuracy DECIMAL(8,6),
    test_roc_auc DECIMAL(8,6),
    test_f1_score DECIMAL(8,6),
    validation_roc_auc DECIMAL(8,6),
    
    -- Training Data Info
    training_records INTEGER NOT NULL,
    validation_records INTEGER NOT NULL,
    test_records INTEGER NOT NULL,
    training_start_date DATE NOT NULL,
    training_end_date DATE NOT NULL,
    
    -- Model File Storage
    model_file_path TEXT NOT NULL,       -- Path to serialized model
    model_file_hash CHAR(64),           -- SHA-256 hash
    model_size_bytes BIGINT,
    feature_names JSONB,                -- Array of feature names
    feature_importance JSONB,           -- XGBoost feature importance scores
    
    -- Status and Lifecycle
    status ml_model_status NOT NULL DEFAULT 'training',
    is_production BOOLEAN NOT NULL DEFAULT FALSE,
    trained_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deployed_at TIMESTAMP WITH TIME ZONE,
    deprecated_at TIMESTAMP WITH TIME ZONE,
    
    -- Airflow Integration
    airflow_dag_id VARCHAR(100),
    airflow_run_id VARCHAR(100),
    training_duration_seconds INTEGER,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL DEFAULT 'airflow',
    
    -- Constraints
    CONSTRAINT unique_instrument_version UNIQUE (instrument_id, model_version),
    CONSTRAINT unique_production_model UNIQUE (instrument_id, is_production) WHERE is_production = TRUE
);

-- Updated enum for model status
CREATE TYPE ml_model_status AS ENUM ('training', 'active', 'deprecated', 'failed', 'testing');
```

#### 2. Feature Engineering Results Table (7-Day System)
```sql
CREATE TABLE IF NOT EXISTS ml_feature_data (
    id BIGSERIAL PRIMARY KEY,
    model_id BIGINT NOT NULL REFERENCES ml_models(id),
    instrument_id INTEGER NOT NULL REFERENCES base_instruments(id),
    
    -- Date Information
    trading_date DATE NOT NULL,
    trading_date_epoch BIGINT NOT NULL,
    
    -- Price Features (OHLCV) - Based on actual DataFrame schema
    open_price DECIMAL(15,6) NOT NULL,
    high_price DECIMAL(15,6) NOT NULL,
    low_price DECIMAL(15,6) NOT NULL,
    close_price DECIMAL(15,6) NOT NULL,
    volume BIGINT NOT NULL,
    
    -- Time Features (From DataFrame analysis)
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    weekday INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_month_end BOOLEAN NOT NULL,
    
    -- Technical Indicators (Top 20 - Based on actual DataFrame)
    rsi_14 DECIMAL(8,4),
    macd_line DECIMAL(8,4),
    macd_signal DECIMAL(8,4),
    macd_histogram DECIMAL(8,4),
    bollinger_upper DECIMAL(15,6),
    bollinger_lower DECIMAL(15,6),
    bollinger_percent DECIMAL(8,4),
    sma_5 DECIMAL(15,6),
    sma_10 DECIMAL(15,6),
    sma_20 DECIMAL(15,6),
    sma_50 DECIMAL(15,6),
    ema_12 DECIMAL(15,6),
    ema_26 DECIMAL(15,6),
    stoch_k DECIMAL(8,4),
    stoch_d DECIMAL(8,4),
    williams_r DECIMAL(8,4),
    atr_14 DECIMAL(8,4),
    adx_14 DECIMAL(8,4),
    cci_20 DECIMAL(8,4),
    roc_10 DECIMAL(8,4),
    
    -- Volume Features (Based on DataFrame analysis)
    volume_sma_5 DECIMAL(20,2),
    volume_sma_10 DECIMAL(20,2),
    volume_sma_20 DECIMAL(20,2),
    volume_ratio_5d DECIMAL(8,4),
    volume_ratio_10d DECIMAL(8,4),
    
    -- Growth/Returns Features (7-Day System)
    returns_1d DECIMAL(8,6),
    returns_3d DECIMAL(8,6),
    returns_7d DECIMAL(8,6),
    growth_1d DECIMAL(8,6),
    growth_3d DECIMAL(8,6),
    growth_7d DECIMAL(8,6),
    
    -- Additional Features (JSON for remaining ~150 features)
    additional_features JSONB,
    
    -- Target Variables (7-Day System) 
    target BOOLEAN NOT NULL,                    -- Binary classification target (7-day growth > 0)
    growth_future_7d DECIMAL(8,6),             -- Raw 7-day forward growth ratio
    
    -- Data Quality
    feature_completeness DECIMAL(5,4),         -- Percentage of non-null features
    data_quality_score DECIMAL(5,4),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_model_instrument_date UNIQUE (model_id, instrument_id, trading_date)
);
```

#### 3. Model Predictions Table (7-Day System)
```sql
CREATE TABLE IF NOT EXISTS ml_predictions (
    id BIGSERIAL PRIMARY KEY,
    model_id BIGINT NOT NULL REFERENCES ml_models(id),
    instrument_id INTEGER NOT NULL REFERENCES base_instruments(id),
    
    -- Prediction Date Info (7-Day System)
    prediction_date DATE NOT NULL,       -- Date when prediction was made
    target_date DATE NOT NULL,           -- Date being predicted for (7 days ahead)
    prediction_horizon_days INTEGER NOT NULL DEFAULT 7,  -- 7-day prediction horizon
    trading_date_epoch BIGINT NOT NULL,
    
    -- Prediction Results
    predicted_class BOOLEAN NOT NULL,    -- Binary prediction (7-day growth/decline)
    prediction_probability DECIMAL(8,6) NOT NULL,  -- Probability [0,1]
    prediction_confidence DECIMAL(8,6),  -- Model confidence score
    
    -- Feature Contributions (Top 10)
    feature_importance_json JSONB,       -- Top feature contributions to this prediction
    
    -- Actual Outcome (filled after 7 days)
    actual_class BOOLEAN,                -- Actual outcome (if available)
    actual_return_7d DECIMAL(8,6),       -- Actual 7-day return
    actual_growth_7d DECIMAL(8,6),       -- Actual 7-day growth ratio
    prediction_accuracy BOOLEAN,         -- Was prediction correct?
    
    -- Trading Signal (7-Day System)
    trading_signal VARCHAR(10),          -- 'BUY', 'HOLD', 'SELL' based on 7-day prediction
    signal_strength DECIMAL(5,4),        -- Signal strength [0,1]
    holding_period_days INTEGER NOT NULL DEFAULT 7,  -- 7-day holding period
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  -- For outcome updates
    airflow_dag_id VARCHAR(100),
    airflow_run_id VARCHAR(100),
    
    -- Constraints
    CONSTRAINT unique_model_prediction_date UNIQUE (model_id, instrument_id, prediction_date, target_date),
    CONSTRAINT valid_probability CHECK (prediction_probability >= 0 AND prediction_probability <= 1)
);
```

#### 4. Backtesting Results Table (7-Day System)
```sql
CREATE TABLE IF NOT EXISTS ml_backtest_results (
    id BIGSERIAL PRIMARY KEY,
    model_id BIGINT NOT NULL REFERENCES ml_models(id),
    instrument_id INTEGER NOT NULL REFERENCES base_instruments(id),
    
    -- Backtest Configuration (7-Day System)
    backtest_start_date DATE NOT NULL,
    backtest_end_date DATE NOT NULL,
    holding_period_days INTEGER NOT NULL DEFAULT 7,     -- 7-day holding periods
    probability_threshold DECIMAL(5,4) NOT NULL DEFAULT 0.6,
    initial_capital DECIMAL(15,2) NOT NULL DEFAULT 10000.00,
    transaction_cost DECIMAL(6,5) NOT NULL DEFAULT 0.001,  -- 0.1% transaction cost
    
    -- Performance Metrics (7-Day Strategy)
    total_return DECIMAL(8,6),
    annualized_return DECIMAL(8,6),
    sharpe_ratio DECIMAL(8,4),
    max_drawdown DECIMAL(8,6),
    win_rate DECIMAL(5,4),
    profit_factor DECIMAL(8,4),
    
    -- Trading Statistics (7-Day Holdings)
    total_trades INTEGER NOT NULL DEFAULT 0,
    winning_trades INTEGER NOT NULL DEFAULT 0,
    losing_trades INTEGER NOT NULL DEFAULT 0,
    avg_trade_return DECIMAL(8,6),
    avg_trade_duration_days DECIMAL(4,2),  -- Should average ~7 days
    best_trade_return DECIMAL(8,6),
    worst_trade_return DECIMAL(8,6),
    
    -- Risk Metrics
    volatility DECIMAL(8,6),
    var_95 DECIMAL(8,6),                -- Value at Risk (95%)
    calmar_ratio DECIMAL(8,4),
    sortino_ratio DECIMAL(8,4),
    
    -- Trade Details (JSON) - 7-Day Trades
    trade_history JSONB,                -- Detailed trade history with 7-day holdings
    monthly_returns JSONB,              -- Monthly return breakdown
    
    -- Quality Assessment
    backtest_quality VARCHAR(20),       -- 'EXCELLENT', 'GOOD', 'FAIR', 'POOR'
    quality_score DECIMAL(5,4),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    airflow_dag_id VARCHAR(100),
    airflow_run_id VARCHAR(100),
    
    -- Constraints
    CONSTRAINT unique_model_backtest UNIQUE (model_id, instrument_id, backtest_start_date, probability_threshold)
);
```

---

## Phase 2: Updated Database Schema Template

### **Additions to `sql/schema_template.sql.j2`**

```sql
-- ML Pipeline Tables for 7-Day Growth Prediction System
-- Add after existing ETL tables

-- ML model status enum
CREATE TYPE {{ schema_name }}.ml_model_status AS ENUM ('training', 'active', 'deprecated', 'failed', 'testing');

-- ML Models table (insert the full table definition here)
-- ... (full table definitions as above)

-- Performance Indexes for ML Tables
DO $$
BEGIN
    -- ML Models indexes
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_models_instrument_id ON ml_models(instrument_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_models_status ON ml_models(status)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_models_production ON ml_models(is_production) WHERE is_production = TRUE';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_models_version ON ml_models(model_version)';
    
    -- Feature data indexes (time-series optimized)
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_feature_data_instrument_date ON ml_feature_data(instrument_id, trading_date DESC)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_feature_data_model_id ON ml_feature_data(model_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_feature_data_date_epoch ON ml_feature_data(trading_date_epoch)';
    
    -- Predictions indexes (7-day system)
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_predictions_instrument_target ON ml_predictions(instrument_id, target_date DESC)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_predictions_model_id ON ml_predictions(model_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_predictions_signal ON ml_predictions(trading_signal, prediction_date)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_predictions_accuracy ON ml_predictions(prediction_accuracy) WHERE prediction_accuracy IS NOT NULL';
    
    -- Backtesting indexes
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_backtest_instrument_id ON ml_backtest_results(instrument_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_backtest_model_id ON ml_backtest_results(model_id)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_ml_backtest_quality ON ml_backtest_results(backtest_quality)';
END $$;
```

---

## Phase 3: Dynamic Airflow DAG Architecture (7-Day System)

### **Updated DAG Task Flow**

```python
# DAG Task Flow for each stock (7-Day System):
1. check_data_availability        # Validate sufficient historical data (7-day system)
2. extract_stock_data            # Extract from stock_prices table  
3. engineer_features_7d          # Create 183 technical indicators + 7-day targets
4. prepare_training_data_7d      # Split and preprocess (7-day targets)
5. train_xgboost_7d             # XGBoost training (7-day growth prediction)
6. validate_model_7d            # Performance validation (ROC-AUC >= 0.55)
7. save_model_artifacts_7d      # Store model + 193 features + predictions
8. run_backtesting_7d          # 7-day holding period strategy evaluation
9. update_model_registry       # Update ml_models table with 7-day config
10. generate_predictions_7d    # Generate 7-day ahead predictions
11. cleanup_old_models         # Archive deprecated models
```

### **Updated DAG Template (Key Changes)**

```python
# stock_etl/airflow_dags/ml_dag_template_7d.py

def create_ml_dag_7d(symbol: str, instrument_id: int) -> DAG:
    """Create ML training DAG for 7-day growth prediction"""
    
    dag_id = f"ml_training_7d_{symbol.lower()}"
    
    with DAG(
        dag_id=dag_id,
        # ... dag configuration
        tags=['ml_pipeline', 'training', '7day_targets', symbol.lower()]
    ) as dag:
        
        @task(task_id=f'engineer_features_7d_{symbol}')
        def engineer_features_7d(data_path: str, **context) -> str:
            """Generate 183 technical indicators with 7-day targets"""
            from stock_ml.feature_engineering import StockFeatureEngineer
            
            feature_engineer = StockFeatureEngineer()
            
            # Load data
            df = pd.read_parquet(data_path)
            
            # Engineer features with 7-day targets
            features_df = feature_engineer.engineer_features(
                df=df,
                symbol=symbol,
                target_days=7  # 7-day targets
            )
            
            # Save features to database
            save_features_to_db(features_df, instrument_id, context)
            
            return features_path
        
        @task(task_id=f'train_model_7d_{symbol}')
        def train_model_7d(features_path: str, **context) -> Dict[str, Any]:
            """Train XGBoost model for 7-day growth prediction"""
            from stock_ml.model_trainer_optimized import HighPerformanceXGBoostTrainer
            
            trainer = HighPerformanceXGBoostTrainer()
            
            # Load preprocessed data
            processed_data = load_preprocessed_data(features_path)
            
            # Train model
            results = trainer.train_and_evaluate(
                **processed_data,
                symbol=symbol,
                grid_type='quick'  # or 'full' for production
            )
            
            # Save model to database
            model_id = save_model_to_db(results, instrument_id, context)
            results['model_id'] = model_id
            
            return results
        
        @task(task_id=f'backtest_7d_{symbol}')
        def run_backtesting_7d(model_id: int, **context) -> Dict[str, Any]:
            """Run 7-day holding period backtesting"""
            from stock_ml.backtesting import TradingBacktester
            
            backtester = TradingBacktester(
                holding_period_days=7,  # 7-day holding periods
                transaction_cost=0.001
            )
            
            # Run backtesting
            results = backtester.backtest_strategy(
                test_df=test_df,
                predictions=predictions,
                probabilities=probabilities,
                symbol=symbol
            )
            
            # Save to database
            save_backtest_to_db(results, model_id, instrument_id, context)
            
            return results
```

---

## Phase 4: Implementation Roadmap (Updated)

### **Stage 1: Database Schema Updates (Week 1)**
1. ✅ **Complete 7-day target refactoring** across all ML modules
2. **Update schema template** with ML tables (7-day system)
3. **Create migration scripts** for test_stock_data schema
4. **Add ML-specific indexes** for 193-column feature data

### **Stage 2: ML Database Integration (Week 2)**
1. **Create ML data models** (Pydantic) for 7-day system
2. **Implement database operations** for ML artifacts storage
3. **Add model versioning** (v2.x.x for 7-day system)
4. **Test feature data storage** (3.43 MB per stock)

### **Stage 3: Airflow DAG Development (Week 3)**
1. **Create 7-day DAG templates** with updated task flow
2. **Implement dynamic DAG generation** for 10 stocks
3. **Add controller DAG** for orchestration
4. **Configure 7-day specific monitoring**

### **Stage 4: Testing & Production (Week 4)**
1. **Test 7-day prediction pipeline**
2. **Validate backtesting with 7-day holdings**
3. **Performance optimization** for 193-feature processing
4. **Deploy production DAGs**

---

## Success Metrics (Updated for 7-Day System)

### **Technical Metrics**
- **Pipeline Success Rate**: >95% successful daily runs
- **Model Performance**: Average ROC-AUC >0.58 across all stocks (better with 7-day targets)
- **Training Speed**: <30 minutes per stock (183 features + 7-day targets)
- **Data Coverage**: 100% feature completeness for 193 columns

### **Business Metrics (7-Day System)**
- **Prediction Accuracy**: >58% correct 7-day growth predictions (improved)
- **Backtest Performance**: >12% annualized returns with 7-day holdings
- **Trading Frequency**: ~4-5 trades per month per stock (7-day holdings)
- **Model Reliability**: <3% model failures (more stable with 7-day targets)

---

## **Key Implementation Advantages**

### **7-Day Target Benefits** ✅ CONFIRMED
1. **Better Model Performance**: 7-day targets produce superior models
2. **More Predictable Patterns**: Weekly market cycles alignment
3. **Higher Trading Frequency**: More opportunities with shorter horizon
4. **Reduced Market Noise**: Less affected by long-term volatility
5. **Faster Validation**: 7-day feedback loop for model improvement

### **DataFrame-Driven Design** ✅ VERIFIED
1. **Actual Schema**: Based on real 193-column DataFrame structure
2. **Confirmed Storage**: 3.43 MB per stock for complete features
3. **Proven Pipeline**: Documented 183 engineered features working
4. **Performance Ready**: Optimized for XGBoost with GPU acceleration

---

*This updated plan reflects the completed 7-day target refactoring and provides a production-ready roadmap for automated multi-stock ML training with improved prediction accuracy.*