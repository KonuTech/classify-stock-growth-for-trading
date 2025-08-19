# Random Forest Stock Growth Classification - Implementation Plan

## Project Overview
**Objective:** Build a robust Random Forest classifier to predict 30-day positive stock growth for trading decisions based on XTB stock historical data.

**Target Variable:** Binary classification - positive growth in 30 days (1) vs non-positive growth (0)
**Initial Dataset:** XTB stock data from existing PostgreSQL tables (no new tables created)
**Data Split:** 60% train, 20% validation, 20% test (chronological order preserved)

## 1. Data Foundation ✅

### Base Data Query
```sql
-- Source data extraction (2,306 records available)
query = """
SELECT
    bi.symbol,
    bi.currency,
    sp.close_price,
    sp.volume,
    sp.trading_date_local
FROM
    test_stock_data.base_instruments AS bi
JOIN
    test_stock_data.stock_prices AS sp ON bi.id = sp.stock_id
WHERE
    bi.symbol = 'XTB'
ORDER BY
    sp.trading_date_local ASC;
"""
```

**Available Data:** 
- Symbol: XTB
- Date range: 2016-05-06 to 2025-08-19 (2,306 records)
- Fields: symbol, currency, close_price, volume, trading_date_local
- Quality: Complete time series, no missing values

### Data Splitting Strategy
```python
# Time series split preserving chronological order
train_size = int(0.6 * len(df))  # 1,384 records (2016-2020)
val_size = int(0.2 * len(df))    # 461 records (2020-2022) 
test_size = len(df) - train_size - val_size  # 461 records (2022-2025)

train_df = df.iloc[:train_size]
val_df = df.iloc[train_size:train_size + val_size]
test_df = df.iloc[train_size + val_size:]
```

## 2. Feature Engineering Pipeline

### Phase 1: Core Features from Close Price and Volume

#### Target Variable Creation
```python
def create_target_variable(df):
    """Create 30-day future growth target"""
    # 30-day forward growth rate
    df['growth_future_30d'] = df['close_price'].shift(-30) / df['close_price']
    
    # Binary target: 1 if positive growth, 0 otherwise
    df['target'] = (df['growth_future_30d'] > 1).astype(int)
    
    # Remove last 30 rows (no future data available)
    df = df.iloc[:-30].copy()
    
    return df
```

#### Time-Based Features (6 features)
```python
def create_time_features(df):
    """Generate time-based features from date"""
    df['trading_date_local'] = pd.to_datetime(df['trading_date_local'])
    
    df['year'] = df['trading_date_local'].dt.year
    df['month'] = df['trading_date_local'].dt.month
    df['weekday'] = df['trading_date_local'].dt.weekday
    df['quarter'] = df['trading_date_local'].dt.quarter
    df['day_of_year'] = df['trading_date_local'].dt.dayofyear
    df['week_of_year'] = df['trading_date_local'].dt.isocalendar().week
    
    return df
```

#### Multi-Timeframe Growth Features (6 features)
```python
def create_growth_features(df):
    """Generate historical growth rates"""
    for period in [1, 3, 7, 30, 90, 365]:
        df[f'growth_{period}d'] = df['close_price'] / df['close_price'].shift(period)
        
    return df
```

#### Price-Based Technical Indicators (10 features)
```python
def create_price_indicators(df):
    """Generate technical indicators from close price only"""
    # Moving averages
    df['sma_5'] = df['close_price'].rolling(5).mean()
    df['sma_10'] = df['close_price'].rolling(10).mean()
    df['sma_20'] = df['close_price'].rolling(20).mean()
    df['sma_50'] = df['close_price'].rolling(50).mean()
    
    # Price relative to moving averages
    df['price_to_sma_10'] = df['close_price'] / df['sma_10']
    df['price_to_sma_20'] = df['close_price'] / df['sma_20']
    
    # Moving average signals
    df['sma_10_above_20'] = (df['sma_10'] > df['sma_20']).astype(int)
    df['price_above_sma_20'] = (df['close_price'] > df['sma_20']).astype(int)
    
    # Volatility and momentum
    df['daily_return'] = df['close_price'].pct_change()
    df['volatility_20d'] = df['daily_return'].rolling(20).std() * np.sqrt(252)
    
    return df
```

#### Volume-Based Features (6 features)
```python
def create_volume_features(df):
    """Generate volume-based indicators"""
    # Volume moving averages
    df['volume_ma_10'] = df['volume'].rolling(10).mean()
    df['volume_ma_20'] = df['volume'].rolling(20).mean()
    
    # Volume relative to averages
    df['volume_ratio_10d'] = df['volume'] / df['volume_ma_10']
    df['volume_ratio_20d'] = df['volume'] / df['volume_ma_20']
    
    # Price-volume relationship
    df['price_volume_trend'] = (df['daily_return'] * df['volume']).rolling(10).mean()
    
    # Volume trend
    df['volume_increasing'] = (df['volume'] > df['volume_ma_20']).astype(int)
    
    return df
```

### Phase 2: Advanced TA-Lib Features (Simulated from Close Price)

#### Simulated OHLC Creation
```python
def simulate_ohlc_from_close(df):
    """Create estimated OHLC data from close prices for TA-Lib compatibility"""
    # Use previous close as open (gap-less assumption)
    df['open_price'] = df['close_price'].shift(1)
    
    # Estimate high/low based on volatility
    daily_volatility = df['close_price'].pct_change().rolling(20).std()
    
    # High = close * (1 + random factor * volatility)
    df['high_price'] = df['close_price'] * (1 + 0.5 * daily_volatility)
    
    # Low = close * (1 - random factor * volatility) 
    df['low_price'] = df['close_price'] * (1 - 0.5 * daily_volatility)
    
    # Ensure OHLC relationships: High >= Open,Close and Low <= Open,Close
    df['high_price'] = df[['high_price', 'close_price', 'open_price']].max(axis=1)
    df['low_price'] = df[['low_price', 'close_price', 'open_price']].min(axis=1)
    
    return df
```

#### Essential TA-Lib Indicators (20 features)
```python
import talib

def create_talib_features(df):
    """Generate TA-Lib indicators from simulated OHLCV"""
    # Momentum indicators
    df['rsi_14'] = talib.RSI(df['close_price'], timeperiod=14)
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close_price'])
    
    # Trend indicators
    df['adx'] = talib.ADX(df['high_price'], df['low_price'], df['close_price'], timeperiod=14)
    df['cci'] = talib.CCI(df['high_price'], df['low_price'], df['close_price'], timeperiod=14)
    
    # Volatility indicators
    df['atr'] = talib.ATR(df['high_price'], df['low_price'], df['close_price'], timeperiod=14)
    df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'] = talib.BBANDS(df['close_price'])
    
    # Volume indicators
    df['obv'] = talib.OBV(df['close_price'], df['volume'])
    df['ad_line'] = talib.AD(df['high_price'], df['low_price'], df['close_price'], df['volume'])
    
    # Oscillators
    df['stoch_k'], df['stoch_d'] = talib.STOCH(df['high_price'], df['low_price'], df['close_price'])
    df['williams_r'] = talib.WILLR(df['high_price'], df['low_price'], df['close_price'], timeperiod=14)
    
    # Rate of change
    df['roc_10'] = talib.ROC(df['close_price'], timeperiod=10)
    df['momentum_10'] = talib.MOM(df['close_price'], timeperiod=10)
    
    # Price transforms
    df['typical_price'] = talib.TYPPRICE(df['high_price'], df['low_price'], df['close_price'])
    df['weighted_close'] = talib.WCLPRICE(df['high_price'], df['low_price'], df['close_price'])
    
    return df
```

### Phase 3: Complete Feature Engineering Pipeline

```python
class XTBFeatureEngineer:
    def __init__(self, db_connection_string):
        self.db_connection = db_connection_string
        
    def extract_raw_data(self):
        """Extract XTB data using the specified query"""
        query = """
        SELECT
            bi.symbol,
            bi.currency,
            sp.close_price,
            sp.volume,
            sp.trading_date_local
        FROM
            test_stock_data.base_instruments AS bi
        JOIN
            test_stock_data.stock_prices AS sp ON bi.id = sp.stock_id
        WHERE
            bi.symbol = 'XTB'
        ORDER BY
            sp.trading_date_local ASC;
        """
        
        import pandas as pd
        from sqlalchemy import create_engine
        
        engine = create_engine(self.db_connection)
        df = pd.read_sql_query(query, engine)
        
        print(f"Extracted {len(df)} records for {df['symbol'].iloc[0]}")
        print(f"Date range: {df['trading_date_local'].min()} to {df['trading_date_local'].max()}")
        
        return df
    
    def engineer_all_features(self, df):
        """Apply complete feature engineering pipeline"""
        print("Starting feature engineering pipeline...")
        
        # Core transformations
        df = create_time_features(df)
        df = create_growth_features(df)
        df = create_price_indicators(df)
        df = create_volume_features(df)
        
        # Simulate OHLC for TA-Lib
        df = simulate_ohlc_from_close(df)
        
        # TA-Lib indicators
        df = create_talib_features(df)
        
        # Create target variable (must be last)
        df = create_target_variable(df)
        
        print(f"Feature engineering complete. Shape: {df.shape}")
        print(f"Target distribution: {df['target'].value_counts(normalize=True)}")
        
        return df
        
    def split_data(self, df):
        """Split data chronologically into train/val/test"""
        # Remove rows with NaN (from rolling calculations)
        df_clean = df.dropna().copy()
        
        n = len(df_clean)
        train_size = int(0.6 * n)
        val_size = int(0.2 * n)
        
        train_df = df_clean.iloc[:train_size].copy()
        val_df = df_clean.iloc[train_size:train_size + val_size].copy()
        test_df = df_clean.iloc[train_size + val_size:].copy()
        
        print(f"Data split:")
        print(f"  Train: {len(train_df)} records ({train_df['trading_date_local'].min()} to {train_df['trading_date_local'].max()})")
        print(f"  Val:   {len(val_df)} records ({val_df['trading_date_local'].min()} to {val_df['trading_date_local'].max()})")
        print(f"  Test:  {len(test_df)} records ({test_df['trading_date_local'].min()} to {test_df['trading_date_local'].max()})")
        
        return train_df, val_df, test_df
```

## 3. Random Forest Model Pipeline

### Data Preprocessing for Random Forest
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectFromModel
import numpy as np

class RandomForestPreprocessor:
    def __init__(self):
        self.imputer = SimpleImputer(strategy='median')
        self.feature_selector = None
        self.feature_columns = None
        
    def prepare_features(self, df):
        """Prepare feature matrix for Random Forest"""
        # Define feature columns (exclude metadata and target)
        exclude_cols = ['symbol', 'currency', 'trading_date_local', 'target', 
                       'growth_future_30d', 'open_price', 'high_price', 'low_price']
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[feature_cols].copy()
        y = df['target'].copy()
        
        # Handle missing values
        X = pd.DataFrame(
            self.imputer.fit_transform(X),
            columns=X.columns,
            index=X.index
        )
        
        self.feature_columns = feature_cols
        print(f"Prepared {X.shape[1]} features for training")
        
        return X, y
        
    def select_features(self, X_train, y_train, n_features=50):
        """Select top features using Random Forest feature importance"""
        # Initial RF for feature selection
        rf_selector = RandomForestClassifier(
            n_estimators=100, 
            random_state=42,
            n_jobs=-1
        )
        
        # Fit and select features
        self.feature_selector = SelectFromModel(
            rf_selector, 
            max_features=n_features,
            threshold=-np.inf  # Select top n_features
        )
        
        X_train_selected = self.feature_selector.fit_transform(X_train, y_train)
        
        # Get selected feature names
        selected_features = np.array(self.feature_columns)[self.feature_selector.get_support()]
        
        print(f"Selected {len(selected_features)} features:")
        print(list(selected_features))
        
        return X_train_selected, selected_features
```

### Model Training and Hyperparameter Optimization
```python
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE

class XTBRandomForestTrainer:
    def __init__(self):
        self.model = None
        self.preprocessor = RandomForestPreprocessor()
        self.selected_features = None
        
    def train_model(self, train_df, val_df):
        """Train Random Forest with hyperparameter optimization"""
        # Prepare training data
        X_train, y_train = self.preprocessor.prepare_features(train_df)
        X_val, y_val = self.preprocessor.prepare_features(val_df)
        
        # Feature selection
        X_train_selected, self.selected_features = self.preprocessor.select_features(
            X_train, y_train, n_features=50
        )
        X_val_selected = self.preprocessor.feature_selector.transform(X_val)
        
        # Handle class imbalance with SMOTE
        print(f"Original class distribution: {np.bincount(y_train)}")
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train_selected, y_train)
        print(f"Balanced class distribution: {np.bincount(y_train_balanced)}")
        
        # Hyperparameter grid
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'class_weight': ['balanced', None]
        }
        
        # Grid search with cross-validation
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        
        grid_search = GridSearchCV(
            rf, 
            param_grid, 
            cv=5, 
            scoring='roc_auc',
            n_jobs=-1,
            verbose=1
        )
        
        print("Starting hyperparameter optimization...")
        grid_search.fit(X_train_balanced, y_train_balanced)
        
        self.model = grid_search.best_estimator_
        
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best CV score: {grid_search.best_score_:.4f}")
        
        # Validate on validation set
        val_predictions = self.model.predict(X_val_selected)
        val_probabilities = self.model.predict_proba(X_val_selected)[:, 1]
        
        print("\nValidation Set Performance:")
        print(classification_report(y_val, val_predictions))
        
        return self.model
        
    def evaluate_model(self, test_df):
        """Evaluate model on test set"""
        X_test, y_test = self.preprocessor.prepare_features(test_df)
        X_test_selected = self.preprocessor.feature_selector.transform(X_test)
        
        # Predictions
        test_predictions = self.model.predict(X_test_selected)
        test_probabilities = self.model.predict_proba(X_test_selected)[:, 1]
        
        print("Test Set Performance:")
        print(classification_report(y_test, test_predictions))
        
        # Feature importance analysis
        feature_importance = pd.DataFrame({
            'feature': self.selected_features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))
        
        return {
            'predictions': test_predictions,
            'probabilities': test_probabilities,
            'actual': y_test,
            'feature_importance': feature_importance
        }
```

## 4. Trading Strategy Backtesting

```python
def backtest_trading_strategy(test_results, test_df, threshold=0.5):
    """Backtest trading strategy based on model predictions"""
    predictions = test_results['probabilities'] >= threshold
    actual_returns = test_df.iloc[-len(predictions):]['growth_future_30d'] - 1
    
    # Strategy returns: only trade when model predicts positive growth
    strategy_returns = np.where(predictions, actual_returns, 0)
    
    # Calculate performance metrics
    total_trades = predictions.sum()
    winning_trades = (strategy_returns > 0).sum()
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    cumulative_return = (1 + strategy_returns).prod() - 1
    avg_return_per_trade = strategy_returns[strategy_returns != 0].mean()
    
    print(f"Trading Strategy Backtest Results:")
    print(f"  Total trades: {total_trades}")
    print(f"  Winning trades: {winning_trades}")
    print(f"  Win rate: {win_rate:.2%}")
    print(f"  Cumulative return: {cumulative_return:.2%}")
    print(f"  Average return per trade: {avg_return_per_trade:.2%}")
    
    return {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'cumulative_return': cumulative_return,
        'avg_return_per_trade': avg_return_per_trade
    }
```

## 5. Complete Implementation Script

```python
def main():
    """Complete XTB Random Forest training pipeline"""
    # Database connection
    DB_CONNECTION = "postgresql://postgres:postgres@localhost:5432/stock_data"
    
    # Initialize feature engineer
    feature_engineer = XTBFeatureEngineer(DB_CONNECTION)
    
    # Extract and engineer features
    raw_data = feature_engineer.extract_raw_data()
    engineered_data = feature_engineer.engineer_all_features(raw_data)
    
    # Split data chronologically
    train_df, val_df, test_df = feature_engineer.split_data(engineered_data)
    
    # Train Random Forest model
    trainer = XTBRandomForestTrainer()
    model = trainer.train_model(train_df, val_df)
    
    # Evaluate on test set
    test_results = trainer.evaluate_model(test_df)
    
    # Backtest trading strategy
    strategy_results = backtest_trading_strategy(test_results, test_df)
    
    print("\n" + "="*50)
    print("XTB STOCK GROWTH CLASSIFICATION - COMPLETE")
    print("="*50)
    
    return {
        'model': model,
        'feature_engineer': feature_engineer,
        'trainer': trainer,
        'test_results': test_results,
        'strategy_results': strategy_results
    }

if __name__ == "__main__":
    results = main()
```

## 6. Success Criteria & Next Steps

### Performance Targets
- **Classification Accuracy:** > 55% (baseline: 50%)
- **Trading Win Rate:** > 45%
- **Precision:** > 60% (minimize false positives)
- **ROC-AUC:** > 0.65

### Implementation Phases
1. **Phase 1:** Basic feature engineering and model training (Week 1)
2. **Phase 2:** TA-Lib integration and feature optimization (Week 2)  
3. **Phase 3:** Model tuning and backtesting (Week 3)
4. **Phase 4:** Production pipeline and storage design (Week 4)

### Future Enhancements
- **Data Storage:** Design PostgreSQL tables for engineered features
- **Multi-Stock Extension:** Apply pipeline to multiple Polish stocks
- **Real-time Pipeline:** Implement daily prediction updates
- **Advanced Features:** Economic indicators and market sentiment

This plan uses only the existing data from your SQL query, transforms it comprehensively using both basic and TA-Lib indicators, and provides a complete Random Forest classification pipeline with proper train/validation/test splits.