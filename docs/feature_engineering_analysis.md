# Feature Engineering Analysis - Module 02 Colab Notebook

## Overview
This document analyzes the feature engineering techniques used in the `[2025]_Module_02_Colab_Working_with_the_data.ipynb` notebook from a different project, focusing on techniques applicable to stock growth classification for trading.

**Analysis Date:** August 19, 2025  
**Source:** Module 02 Colab Notebook - Working with Financial Data  
**Focus:** Feature engineering techniques for time series financial data

## Key Feature Engineering Techniques Identified

### 1. Time Series Lag Features (Shift Operations)

**Purpose:** Create historical and future-looking features from time series data.

```python
# Historical and future shifted values
nvo_df['close_minus_1'] = nvo_df['Close'].shift(-1)  # Future value (t+1)
nvo_df['close_plus_1'] = nvo_df['Close'].shift(1)    # Past value (t-1)
```

**Applications:**
- Create lagged price features for temporal dependencies
- Generate future target variables for supervised learning
- Build autoregressive features

### 2. Growth Rate Features (Multiple Time Windows)

**Purpose:** Capture price momentum across different time horizons.

```python
# Historical growth rates over different periods
nvo_df['growth_1d'] = nvo_df['Close'] / nvo_df['Close'].shift(1)
nvo_df['growth_30d'] = nvo_df['Close'] / nvo_df['Close'].shift(30)

# Future growth rates (for prediction targets)
nvo_df['growth_future_1d'] = nvo_df['Close'].shift(-1) / nvo_df['Close']
nvo_df['growth_future_30d'] = nvo_df['Close'].shift(-30) / nvo_df['Close']

# Multiple timeframe growth features using loop
for i in [1,3,7,30,90,365]:
    dax_daily['growth_dax_'+str(i)+'d'] = dax_daily['Close'] / dax_daily['Close'].shift(i)
```

**Key Characteristics:**
- Uses ratio-based features instead of absolute values
- Multi-timeframe approach (1, 3, 7, 30, 90, 365 days)
- Forward-looking features for target variable creation

### 3. Binary Classification Features

**Purpose:** Convert continuous variables to binary signals for classification tasks.

```python
# Convert continuous growth to binary outcomes
nvo_df['is_positive_growth_1d_future'] = np.where(nvo_df['growth_future_1d'] > 1, 1, 0)
nvo_df['is_positive_growth_30d_future'] = np.where(nvo_df['growth_future_30d'] > 1, 1, 0)
```

**Applications:**
- Create binary target variables for classification
- Generate trading signals (buy/sell/hold)
- Simplify complex continuous relationships

### 4. Moving Averages and Technical Indicators

**Purpose:** Smooth price data and identify trend directions.

```python
# Simple Moving Averages
historyPrices['SMA10'] = historyPrices['Close'].rolling(10).mean()
historyPrices['SMA20'] = historyPrices['Close'].rolling(20).mean()

# Moving average crossover signal
historyPrices['growing_moving_average'] = np.where(historyPrices['SMA10'] > historyPrices['SMA20'], 1, 0)
```

**Features Created:**
- Short-term and long-term trend indicators
- Crossover signals for trend changes
- Support/resistance level identification

### 5. Volatility Features

**Purpose:** Measure price variability and market uncertainty.

```python
# 30-day rolling volatility (annualized)
historyPrices['volatility'] = historyPrices['Close'].rolling(30).std() * np.sqrt(252)
```

**Applications:**
- Risk assessment features
- Market regime identification
- Portfolio optimization inputs

### 6. Price Range Features

**Purpose:** Capture intraday price movement characteristics.

```python
# Relative price range (normalized by closing price)
historyPrices['high_minus_low_relative'] = (historyPrices.High - historyPrices.Low) / historyPrices['Close']
```

**Benefits:**
- Scale-invariant features
- Measure of daily trading activity
- Volatility proxy

### 7. Economic Indicator Features

**Purpose:** Incorporate macroeconomic factors into stock analysis.

```python
# Year-over-year and quarter-over-quarter changes
gdppot['gdppot_us_yoy'] = gdppot.GDPPOT/gdppot.GDPPOT.shift(4)-1  # YoY
gdppot['gdppot_us_qoq'] = gdppot.GDPPOT/gdppot.GDPPOT.shift(1)-1  # QoQ

# Consumer Price Index features
cpilfesl['cpi_core_yoy'] = cpilfesl.CPILFESL/cpilfesl.CPILFESL.shift(12)-1  # YoY
cpilfesl['cpi_core_mom'] = cpilfesl.CPILFESL/cpilfesl.CPILFESL.shift(1)-1   # MoM
```

**Economic Features:**
- GDP growth rates
- Inflation indicators (CPI)
- Interest rate changes
- Employment metrics

### 8. Categorical Encoding

**Purpose:** Convert categorical variables to numerical features.

```python
# Geographic/market categorization
stocks_df['ticker_type'] = stocks_df.Ticker.apply(lambda x:get_ticker_type(x, US_STOCKS, EU_STOCKS, INDIA_STOCKS))
```

**Applications:**
- Market segment classification
- Geographic exposure features
- Sector/industry encoding

### 9. Reusable Feature Engineering Functions

**Purpose:** Create modular, reusable feature engineering pipelines.

```python
def get_growth_df(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Generate growth features for multiple timeframes"""
    for i in [1,3,7,30,90,365]:
        df['growth_'+prefix+'_'+str(i)+'d'] = df['Close'] / df['Close'].shift(i)
        GROWTH_KEYS = [k for k in df.keys() if k.startswith('growth')]
    return df
```

**Benefits:**
- Code reusability across different assets
- Consistent feature generation
- Easy parameter modification

## Feature Engineering Patterns

### 1. Multi-timeframe Analysis
- Features created across various time windows (1, 3, 7, 30, 90, 365 days)
- Captures both short-term momentum and long-term trends
- Allows model to learn patterns at different frequencies

### 2. Forward-looking Target Creation
- Future prices shifted backward to create prediction targets
- Enables supervised learning setup for time series
- Prevents data leakage in model training

### 3. Ratio-based Normalization
- Most features are ratios rather than absolute values
- Scale-invariant across different price levels
- Better generalization across different stocks

### 4. Signal Generation
- Converting continuous features to binary signals
- Simplifies decision boundaries for classification
- Creates interpretable trading rules

### 5. Cross-asset Feature Integration
- Combines individual stock features with market indices
- Incorporates economic indicators as external features
- Captures broader market context

## Technical Implementation Notes

### Data Handling
- Uses pandas shift() operations for time series transformations
- Applies defensive programming with error handling (`errors='coerce'`)
- Implements proper datetime indexing for time series operations

### Performance Considerations
- Vectorized operations using pandas and numpy
- Batch processing of multiple timeframes using loops
- Efficient memory usage with appropriate data types

### Missing Data Strategy
- Uses `pd.to_numeric()` with `errors='coerce'` for robust data conversion
- Implements forward-fill and backward-fill strategies where appropriate
- Handles missing values in rolling calculations

## Recommendations for Stock Growth Classification

### High-Priority Features
1. **Multi-timeframe growth rates** - Essential for momentum analysis
2. **Moving average crossovers** - Strong trend indicators
3. **Volatility measures** - Important for risk assessment
4. **Binary classification targets** - For clear buy/sell signals

### Medium-Priority Features
1. **Economic indicators** - For market context
2. **Price range features** - For intraday patterns
3. **Categorical encodings** - For sector/market effects

### Advanced Considerations
1. **Feature interactions** - Combine multiple indicators
2. **Dynamic time windows** - Adaptive lookback periods
3. **Regime-specific features** - Bull/bear market adjustments
4. **Cross-sectional features** - Relative performance metrics

## Next Steps

1. **Implement core features** - Start with growth rates and moving averages
2. **Validate feature importance** - Use statistical tests and model-based methods
3. **Test temporal stability** - Ensure features work across different market periods
4. **Optimize parameters** - Fine-tune time windows and thresholds
5. **Integrate with TA-Lib** - Expand to professional technical indicators

## References

- Original notebook: `[2025]_Module_02_Colab_Working_with_the_data.ipynb`
- Feature engineering best practices for financial time series
- Technical analysis principles and momentum indicators

## Below are examples of features names, engineered using above algorithms. We aim to build a data frame for random forest classification of future stocks growth. We want to build similiar data frame. Inspire by these column names to deliver new features. Target column: growth_30d:

Open                             
High                             
Low                              
Close_x                          
Volume                           
Dividends                        
Stock Splits                     
Ticker                           
Year                             
Month                         
Weekday                          
Date                          
growth_1d                        
growth_3d                        
growth_7d                        
growth_30d                       
growth_90d                       
growth_365d                      
growth_future_30d                
SMA10                            
SMA20                            
growing_moving_average           
high_minus_low_relative          
volatility                       
is_positive_growth_30d_future    
ticker_type                      
index_x                          
adx                              
adxr                             
apo                              
aroon_1                          
aroon_2                          
aroonosc                         
bop                              
cci                              
cmo                              
dx                               
macd                             
macdsignal                       
macdhist                         
macd_ext                         
macdsignal_ext                   
macdhist_ext                     
macd_fix                         
macdsignal_fix                   
macdhist_fix                     
mfi                              
minus_di                         
mom                              
plus_di                          
dm                               
ppo                              
roc                              
rocp                             
rocr                             
rocr100                          
rsi                              
slowk                            
slowd                            
fastk                            
fastd                            
fastk_rsi                        
fastd_rsi                        
trix                             
ultosc                           
willr                            
index_y                          
ad                               
adosc                            
obv                              
atr                              
natr                             
ht_dcperiod                      
ht_dcphase                       
ht_phasor_inphase                
ht_phasor_quadrature             
ht_sine_sine                     
ht_sine_leadsine                 
ht_trendmod                      
avgprice                         
medprice                         
typprice                         
wclprice                         
index                            
cdl2crows                        
cdl3blackrows                    
cdl3inside                       
cdl3linestrike                   
cdl3outside                      
cdl3starsinsouth                 
cdl3whitesoldiers                
cdlabandonedbaby                 
cdladvancedblock                 
cdlbelthold                      
cdlbreakaway                     
cdlclosingmarubozu               
cdlconcealbabyswall              
cdlcounterattack                 
cdldarkcloudcover                
cdldoji                          
cdldojistar                      
cdldragonflydoji                 
cdlengulfing                     
cdleveningdojistar               
cdleveningstar                   
cdlgapsidesidewhite              
cdlgravestonedoji                
cdlhammer                        
cdlhangingman                    
cdlharami                        
cdlharamicross                   
cdlhighwave                      
cdlhikkake                       
cdlhikkakemod                    
cdlhomingpigeon                  
cdlidentical3crows               
cdlinneck                        
cdlinvertedhammer                
cdlkicking                       
cdlkickingbylength               
cdlladderbottom                  
cdllongleggeddoji                
cdllongline                      
cdlmarubozu                      
cdlmatchinglow                   
cdlmathold                       
cdlmorningdojistar               
cdlmorningstar                   
cdlonneck                        
cdlpiercing                      
cdlrickshawman                   
cdlrisefall3methods              
cdlseparatinglines               
cdlshootingstar                  
cdlshortline                     
cdlspinningtop                   
cdlstalledpattern                
cdlsticksandwich                 
cdltakuru                        
cdltasukigap                     
cdlthrusting                     
cdltristar                       
cdlunique3river                  
cdlupsidegap2crows               
cdlxsidegap3methods              
growth_dax_1d                    
growth_dax_3d                    
growth_dax_7d                    
growth_dax_30d                   
growth_dax_90d                   
growth_dax_365d                  
growth_snp500_1d                 
growth_snp500_3d                 
growth_snp500_7d                 
growth_snp500_30d                
growth_snp500_90d                
growth_snp500_365d               
growth_dji_1d                    
growth_dji_3d                    
growth_dji_7d                    
growth_dji_30d                   
growth_dji_90d                   
growth_dji_365d                  
growth_epi_1d                    
growth_epi_3d                    
growth_epi_7d                    
growth_epi_30d                   
growth_epi_90d                   
growth_epi_365d                  
Quarter                       
gdppot_us_yoy                    
gdppot_us_qoq                    
cpi_core_yoy                     
cpi_core_mom                     
FEDFUNDS                         
DGS1                             
DGS5                             
DGS10                            
Close_y                          
growth_gold_1d                   
growth_gold_3d                   
growth_gold_7d                   
growth_gold_30d                  
growth_gold_90d                  
growth_gold_365d                 
growth_wti_oil_1d                
growth_wti_oil_3d                
growth_wti_oil_7d                
growth_wti_oil_30d               
growth_wti_oil_90d               
growth_wti_oil_365d              
growth_brent_oil_1d              
growth_brent_oil_3d              
growth_brent_oil_7d              
growth_brent_oil_30d             
growth_brent_oil_90d             
growth_brent_oil_365d            
growth_btc_usd_1d                
growth_btc_usd_3d                
growth_btc_usd_7d                
growth_btc_usd_30d               
growth_btc_usd_90d               
growth_btc_usd_365d              


## ✅ Preprocessing techniques that matter for Random Forests
1. Handle missing values

Random Forests in scikit-learn cannot handle NaNs directly.

Options:

Use imputation (SimpleImputer, IterativeImputer, KNNImputer).

Drop features or rows if missingness is extreme.

Some implementations (like XGBoost and CatBoost) can handle missing values internally.

2. Encode categorical variables

Random Forest in scikit-learn does not handle categoricals natively → they must be numeric.

Recommended encodings:

One-Hot Encoding (safe if categories aren’t too many).

Ordinal Encoding (only if categories have a natural order).

Target Encoding (for high-cardinality categories, but watch out for leakage).

CatBoost is a tree model that can handle categoricals directly, so no encoding is needed there.

3. Reduce high cardinality or irrelevant features

Random Forests can get slowed down by many irrelevant features.

Techniques:

VarianceThreshold (remove features with no variance).

SelectFromModel(RandomForestClassifier) or permutation importance to prune features.

Domain-driven filtering (drop IDs, timestamps, etc. unless properly engineered).

4. Feature engineering (when useful)

Binning continuous variables sometimes helps interpretability, but not needed for performance.

Interactions / ratios: If domain knowledge suggests meaningful ratios or differences, Random Forests can benefit.

Date/time features: Extract useful parts (month, weekday, hour, etc.) before feeding in.

5. Outlier handling (sometimes)

Random Forests are less sensitive to outliers than linear models, since splits isolate them quickly.

But if outliers dominate the dataset, trimming/extreme value handling may help.

6. Balance the classes (for classification)

If target is imbalanced, Random Forests may bias toward the majority class.

Options:

Class weights (class_weight='balanced' in sklearn).

⚠️ **For financial time series**: Avoid synthetic resampling (SMOTE, ADASYN) - use class_weight='balanced' instead to preserve temporal integrity.

❌ Preprocessing NOT needed for Random Forests

Feature scaling / normalization → irrelevant.

Polynomial feature expansion → usually unnecessary (trees handle non-linearities naturally).

✅ Summary: For Random Forests, the big three are
👉 Handle missing values,
👉 Encode categoricals properly,
👉 Do feature selection for efficiency/interpretability.

Everything else is optional and dataset-specific.