"""
Feature engineering module for stock growth classification.
Implements comprehensive feature generation from close price and volume data.
"""

import pandas as pd
import numpy as np
import warnings
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import TA-Lib, provide fallback if not available
try:
    import talib
    TALIB_AVAILABLE = True
    logger.info("TA-Lib imported successfully")
except ImportError:
    TALIB_AVAILABLE = False
    logger.warning("TA-Lib not available. Using basic indicators only.")


class StockFeatureEngineer:
    """Feature engineering pipeline for stock data"""
    
    def __init__(self):
        self.feature_names = []
        
    def create_target_variable(self, df: pd.DataFrame, target_days: int = 30) -> pd.DataFrame:
        """
        Create target variable for future growth prediction
        
        Args:
            df: Stock DataFrame with close_price column
            target_days: Number of days to look ahead (default: 30)
            
        Returns:
            DataFrame with target variable added
        """
        df = df.copy()
        
        # 30-day forward growth rate
        df['growth_future_30d'] = df['close_price'].shift(-target_days) / df['close_price']
        
        # Binary target: 1 if positive growth, 0 otherwise
        df['target'] = (df['growth_future_30d'] > 1).astype(int)
        
        # Remove last N rows (no future data available)
        df = df.iloc[:-target_days].copy()
        
        target_distribution = df['target'].value_counts(normalize=True)
        logger.info(f"Target distribution - Positive: {target_distribution.get(1, 0):.2%}, Negative: {target_distribution.get(0, 0):.2%}")
        
        return df
        
    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate time-based features from date"""
        df = df.copy()
        
        # Ensure datetime format
        df['trading_date_local'] = pd.to_datetime(df['trading_date_local'])
        
        df['year'] = df['trading_date_local'].dt.year
        df['month'] = df['trading_date_local'].dt.month
        df['weekday'] = df['trading_date_local'].dt.weekday  # Monday=0, Sunday=6
        df['quarter'] = df['trading_date_local'].dt.quarter
        df['day_of_year'] = df['trading_date_local'].dt.dayofyear
        df['week_of_year'] = df['trading_date_local'].dt.isocalendar().week
        
        # Market timing features
        df['is_month_end'] = (df['trading_date_local'].dt.day >= 25).astype(int)
        df['is_quarter_end'] = df['trading_date_local'].dt.month.isin([3, 6, 9, 12]).astype(int)
        df['is_year_end'] = (df['trading_date_local'].dt.month == 12).astype(int)
        
        time_features = ['year', 'month', 'weekday', 'quarter', 'day_of_year', 
                        'week_of_year', 'is_month_end', 'is_quarter_end', 'is_year_end']
        
        logger.debug(f"Created {len(time_features)} time-based features")
        return df
        
    def create_growth_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate historical growth rate features"""
        df = df.copy()
        
        growth_periods = [1, 3, 7, 14, 30, 60, 90, 180, 365]
        
        for period in growth_periods:
            df[f'growth_{period}d'] = df['close_price'] / df['close_price'].shift(period)
            
        # Growth momentum features
        df['growth_acceleration_7d'] = df['growth_7d'] - df['growth_14d']
        df['growth_acceleration_30d'] = df['growth_30d'] - df['growth_60d']
        
        growth_features = [f'growth_{p}d' for p in growth_periods] + \
                         ['growth_acceleration_7d', 'growth_acceleration_30d']
        
        logger.debug(f"Created {len(growth_features)} growth-based features")
        return df
        
    def create_price_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate technical indicators from close price"""
        df = df.copy()
        
        # Simple Moving Averages
        ma_periods = [5, 10, 20, 50, 100, 200]
        for period in ma_periods:
            df[f'sma_{period}'] = df['close_price'].rolling(period).mean()
            
        # Exponential Moving Averages
        ema_periods = [12, 26, 50]
        for period in ema_periods:
            df[f'ema_{period}'] = df['close_price'].ewm(span=period).mean()
            
        # Price relative to moving averages
        df['price_to_sma_20'] = df['close_price'] / df['sma_20']
        df['price_to_sma_50'] = df['close_price'] / df['sma_50']
        df['price_to_sma_200'] = df['close_price'] / df['sma_200']
        
        # Moving average crossover signals
        df['sma_10_above_20'] = (df['sma_10'] > df['sma_20']).astype(int)
        df['sma_20_above_50'] = (df['sma_20'] > df['sma_50']).astype(int)
        df['sma_50_above_200'] = (df['sma_50'] > df['sma_200']).astype(int)
        df['price_above_sma_20'] = (df['close_price'] > df['sma_20']).astype(int)
        df['price_above_sma_50'] = (df['close_price'] > df['sma_50']).astype(int)
        
        # Returns and volatility
        df['daily_return'] = df['close_price'].pct_change()
        df['daily_return_squared'] = df['daily_return'] ** 2
        
        # Rolling volatility (different periods)
        vol_periods = [5, 10, 20, 30, 60]
        for period in vol_periods:
            df[f'volatility_{period}d'] = df['daily_return'].rolling(period).std() * np.sqrt(252)
            df[f'return_mean_{period}d'] = df['daily_return'].rolling(period).mean()
            
        # Price momentum
        df['price_momentum_5d'] = df['close_price'] - df['close_price'].shift(5)
        df['price_momentum_20d'] = df['close_price'] - df['close_price'].shift(20)
        
        # Price position in recent range
        df['price_position_20d'] = (df['close_price'] - df['close_price'].rolling(20).min()) / \
                                 (df['close_price'].rolling(20).max() - df['close_price'].rolling(20).min())
        df['price_position_60d'] = (df['close_price'] - df['close_price'].rolling(60).min()) / \
                                 (df['close_price'].rolling(60).max() - df['close_price'].rolling(60).min())
        
        price_features = [f'sma_{p}' for p in ma_periods] + \
                        [f'ema_{p}' for p in ema_periods] + \
                        ['price_to_sma_20', 'price_to_sma_50', 'price_to_sma_200',
                         'sma_10_above_20', 'sma_20_above_50', 'sma_50_above_200',
                         'price_above_sma_20', 'price_above_sma_50',
                         'daily_return', 'daily_return_squared'] + \
                        [f'volatility_{p}d' for p in vol_periods] + \
                        [f'return_mean_{p}d' for p in vol_periods] + \
                        ['price_momentum_5d', 'price_momentum_20d',
                         'price_position_20d', 'price_position_60d']
        
        logger.debug(f"Created {len(price_features)} price-based features")
        return df
        
    def create_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate volume-based indicators"""
        df = df.copy()
        
        # Volume moving averages
        vol_ma_periods = [5, 10, 20, 50]
        for period in vol_ma_periods:
            df[f'volume_ma_{period}'] = df['volume'].rolling(period).mean()
            
        # Volume relative to averages
        df['volume_ratio_10d'] = df['volume'] / df['volume_ma_10']
        df['volume_ratio_20d'] = df['volume'] / df['volume_ma_20']
        df['volume_ratio_50d'] = df['volume'] / df['volume_ma_50']
        
        # Volume trend indicators
        df['volume_increasing_10d'] = (df['volume'] > df['volume_ma_10']).astype(int)
        df['volume_increasing_20d'] = (df['volume'] > df['volume_ma_20']).astype(int)
        
        # Price-volume relationship
        df['price_volume_trend_5d'] = (df['daily_return'] * df['volume']).rolling(5).mean()
        df['price_volume_trend_20d'] = (df['daily_return'] * df['volume']).rolling(20).mean()
        
        # Volume momentum
        df['volume_momentum_5d'] = df['volume'] - df['volume'].shift(5)
        df['volume_momentum_20d'] = df['volume'] - df['volume'].shift(20)
        
        # Volume volatility
        df['volume_volatility_20d'] = df['volume'].rolling(20).std() / df['volume_ma_20']
        
        # On-Balance Volume (OBV) approximation
        df['obv_approx'] = np.where(df['daily_return'] > 0, df['volume'], 
                                   np.where(df['daily_return'] < 0, -df['volume'], 0)).cumsum()
        df['obv_ma_20'] = df['obv_approx'].rolling(20).mean()
        
        volume_features = [f'volume_ma_{p}' for p in vol_ma_periods] + \
                         ['volume_ratio_10d', 'volume_ratio_20d', 'volume_ratio_50d',
                          'volume_increasing_10d', 'volume_increasing_20d',
                          'price_volume_trend_5d', 'price_volume_trend_20d',
                          'volume_momentum_5d', 'volume_momentum_20d', 'volume_volatility_20d',
                          'obv_approx', 'obv_ma_20']
        
        logger.debug(f"Created {len(volume_features)} volume-based features")
        return df
        
    def simulate_ohlc_from_close(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create estimated OHLC data from close prices for TA-Lib compatibility"""
        df = df.copy()
        
        # Use previous close as open (gap-less assumption)
        df['open_price'] = df['close_price'].shift(1)
        
        # Estimate high/low based on recent volatility
        daily_volatility = df['close_price'].pct_change().rolling(20).std().fillna(0.02)
        
        # Random factor for high/low estimation (0.3-0.7 of daily volatility)
        np.random.seed(42)  # For reproducibility
        high_factor = 0.3 + 0.4 * np.random.random(len(df))
        low_factor = 0.3 + 0.4 * np.random.random(len(df))
        
        # High = close * (1 + factor * volatility)
        df['high_price'] = df['close_price'] * (1 + high_factor * daily_volatility)
        
        # Low = close * (1 - factor * volatility)
        df['low_price'] = df['close_price'] * (1 - low_factor * daily_volatility)
        
        # Ensure OHLC relationships: High >= Open,Close and Low <= Open,Close
        df['high_price'] = df[['high_price', 'close_price', 'open_price']].max(axis=1)
        df['low_price'] = df[['low_price', 'close_price', 'open_price']].min(axis=1)
        
        # Fill NaN in open_price (first row)
        df['open_price'] = df['open_price'].fillna(df['close_price'])
        
        return df
        
    def create_talib_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate TA-Lib technical indicators (if available)"""
        if not TALIB_AVAILABLE:
            logger.warning("TA-Lib not available, skipping advanced indicators")
            return df
            
        df = df.copy()
        
        # Ensure we have OHLC data
        if 'open_price' not in df.columns:
            df = self.simulate_ohlc_from_close(df)
            
        # Convert to numpy arrays for TA-Lib (ensure float64 type)
        high = df['high_price'].astype('float64').values
        low = df['low_price'].astype('float64').values
        close = df['close_price'].astype('float64').values
        volume = df['volume'].astype('float64').values
        open_price = df['open_price'].astype('float64').values
        
        try:
            # Momentum Indicators
            df['rsi_14'] = talib.RSI(close, timeperiod=14)
            df['rsi_7'] = talib.RSI(close, timeperiod=7)
            
            # MACD
            df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(close)
            
            # Stochastic
            df['stoch_k'], df['stoch_d'] = talib.STOCH(high, low, close)
            df['stoch_rsi_k'], df['stoch_rsi_d'] = talib.STOCHRSI(close, timeperiod=14)
            
            # Williams %R
            df['williams_r'] = talib.WILLR(high, low, close, timeperiod=14)
            
            # ADX (Average Directional Index)
            df['adx'] = talib.ADX(high, low, close, timeperiod=14)
            df['plus_di'] = talib.PLUS_DI(high, low, close, timeperiod=14)
            df['minus_di'] = talib.MINUS_DI(high, low, close, timeperiod=14)
            
            # CCI (Commodity Channel Index)
            df['cci'] = talib.CCI(high, low, close, timeperiod=14)
            
            # CMO (Chande Momentum Oscillator)
            df['cmo'] = talib.CMO(close, timeperiod=14)
            
            # ROC (Rate of Change)
            df['roc_10'] = talib.ROC(close, timeperiod=10)
            df['roc_20'] = talib.ROC(close, timeperiod=20)
            
            # MOM (Momentum)
            df['momentum_10'] = talib.MOM(close, timeperiod=10)
            
            # Volatility Indicators
            df['atr'] = talib.ATR(high, low, close, timeperiod=14)
            df['natr'] = talib.NATR(high, low, close, timeperiod=14)
            
            # Bollinger Bands
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(close)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            df['bb_position'] = (close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Volume Indicators
            df['obv'] = talib.OBV(close, volume)
            df['ad_line'] = talib.AD(high, low, close, volume)
            df['mfi'] = talib.MFI(high, low, close, volume, timeperiod=14)
            
            # Price Transform Indicators
            df['typical_price'] = talib.TYPPRICE(high, low, close)
            df['weighted_close'] = talib.WCLPRICE(high, low, close)
            df['median_price'] = talib.MEDPRICE(high, low)
            
            # Overlap Studies (additional moving averages)
            df['dema_20'] = talib.DEMA(close, timeperiod=20)
            df['tema_20'] = talib.TEMA(close, timeperiod=20)
            df['trima_20'] = talib.TRIMA(close, timeperiod=20)
            
            # Pattern Recognition (selected patterns)
            df['cdl_doji'] = talib.CDLDOJI(open_price, high, low, close)
            df['cdl_hammer'] = talib.CDLHAMMER(open_price, high, low, close)
            df['cdl_engulfing'] = talib.CDLENGULFING(open_price, high, low, close)
            df['cdl_morning_star'] = talib.CDLMORNINGSTAR(open_price, high, low, close)
            df['cdl_evening_star'] = talib.CDLEVENINGSTAR(open_price, high, low, close)
            
            talib_features = ['rsi_14', 'rsi_7', 'macd', 'macd_signal', 'macd_hist',
                             'stoch_k', 'stoch_d', 'stoch_rsi_k', 'stoch_rsi_d', 'williams_r',
                             'adx', 'plus_di', 'minus_di', 'cci', 'cmo', 'roc_10', 'roc_20',
                             'momentum_10', 'atr', 'natr', 'bb_upper', 'bb_middle', 'bb_lower',
                             'bb_width', 'bb_position', 'obv', 'ad_line', 'mfi',
                             'typical_price', 'weighted_close', 'median_price',
                             'dema_20', 'tema_20', 'trima_20',
                             'cdl_doji', 'cdl_hammer', 'cdl_engulfing', 'cdl_morning_star', 'cdl_evening_star']
            
            logger.debug(f"Created {len(talib_features)} TA-Lib features")
            
        except Exception as e:
            logger.error(f"Error creating TA-Lib features: {e}")
            
        return df
        
    def clean_invalid_values(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Clean infinite and invalid values from DataFrame"""
        # Replace infinite values with NaN
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Check for very large values that might cause issues
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in df.columns:
                # Replace extremely large values (beyond float64 safe range)
                max_safe_value = 1e10
                df[col] = df[col].clip(-max_safe_value, max_safe_value)
                
        logger.debug(f"{symbol}: Cleaned invalid values")
        return df
        
    def engineer_all_features(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Apply complete feature engineering pipeline"""
        logger.info(f"Starting feature engineering for {symbol}...")
        
        # Ensure we have enough data
        if len(df) < 200:
            logger.warning(f"{symbol}: Insufficient data ({len(df)} records). Need at least 200.")
            return pd.DataFrame()
        
        original_len = len(df)
        
        # Apply feature engineering steps
        df = self.create_time_features(df)
        df = self.create_growth_features(df)
        df = self.create_price_indicators(df)
        df = self.create_volume_features(df)
        df = self.create_talib_features(df)
        
        # Clean invalid values (before target creation)
        df = self.clean_invalid_values(df, symbol)
        
        # Create target variable (must be last step)
        df = self.create_target_variable(df)
        
        # Remove rows with too many NaN values
        df_clean = df.dropna(thresh=len(df.columns) * 0.7)  # Keep rows with at least 70% non-NaN values
        
        features_created = len([col for col in df_clean.columns if col not in 
                              ['symbol', 'currency', 'trading_date_local', 'close_price', 'volume',
                               'open_price', 'high_price', 'low_price', 'target', 'growth_future_30d']])
        
        logger.info(f"{symbol}: Created {features_created} features. "
                   f"Data: {original_len} -> {len(df_clean)} records after cleaning")
        
        return df_clean
        
    def engineer_multiple_stocks(self, all_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Apply feature engineering to multiple stocks"""
        engineered_data = {}
        
        for symbol, df in all_data.items():
            try:
                engineered_df = self.engineer_all_features(df, symbol)
                if not engineered_df.empty:
                    engineered_data[symbol] = engineered_df
                else:
                    logger.warning(f"Skipping {symbol}: Feature engineering failed")
            except Exception as e:
                logger.error(f"Failed to engineer features for {symbol}: {e}")
                continue
                
        logger.info(f"Successfully engineered features for {len(engineered_data)} stocks")
        return engineered_data


if __name__ == "__main__":
    # Test with sample data
    import sys
    sys.path.append('..')
    try:
        from .data_extractor import MultiStockDataExtractor
    except ImportError:
        from data_extractor import MultiStockDataExtractor
    
    # Extract data
    extractor = MultiStockDataExtractor()
    try:
        all_data = extractor.extract_all_stocks_data()
        quality_data = extractor.filter_stocks_by_data_quality(all_data)
        
        # Feature engineering
        engineer = StockFeatureEngineer()
        engineered_data = engineer.engineer_multiple_stocks(quality_data)
        
        # Show results
        for symbol, df in engineered_data.items():
            print(f"{symbol}: {df.shape[0]} records, {df.shape[1]} features")
            if 'target' in df.columns:
                target_dist = df['target'].value_counts(normalize=True)
                print(f"  Target distribution: {target_dist.to_dict()}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        extractor.close()