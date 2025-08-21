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
from pathlib import Path
from scipy.stats import chi2_contingency, f_oneway, pointbiserialr, boxcox
from scipy import signal
from scipy.fftpack import dct, idct
from sklearn.feature_selection import mutual_info_classif, f_classif

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set up logging using centralized configuration
try:
    from .logging_config import get_ml_logger
except ImportError:
    from logging_config import get_ml_logger
logger = get_ml_logger(__name__)

def find_project_root() -> Path:
    """Find project root by looking for CLAUDE.md"""
    current_path = Path(__file__).parent
    while current_path != current_path.parent:
        if (current_path / 'CLAUDE.md').exists():
            return current_path
        current_path = current_path.parent
    return Path(__file__).parent.parent  # Fallback

def document_dataframe(df: pd.DataFrame, name: str, description: str, symbol: str = "GENERIC") -> None:
    """Document DataFrame structure and save to markdown file"""
    
    if df is None or df.empty:
        return
        
    try:
        # Create documentation directory
        project_root = find_project_root()
        docs_dir = project_root / "docs" / "knowledge_base" / "dataframe_schemas"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        shape = df.shape
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        # Column analysis
        columns_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100 if len(df) > 0 else 0
            
            # Sample values for categorical columns
            sample_values = ""
            if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                unique_count = df[col].nunique()
                if unique_count <= 10:
                    top_values = df[col].value_counts().head(3)
                    sample_values = f" | Examples: {', '.join([f'{k}({v})' for k, v in top_values.items()])}"
            
            columns_info.append({
                'column': col,
                'dtype': dtype,
                'null_count': null_count,
                'null_pct': null_pct,
                'sample_values': sample_values
            })
        
        # Key numeric columns for summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        key_numeric_cols = [col for col in numeric_cols if any(
            keyword in col.lower() for keyword in ['price', 'return', 'volume', 'target', 'rsi', 'macd', 'growth']
        )][:10]
        
        # Create markdown content
        md_content = f"""# {name.title().replace('_', ' ')} DataFrame Schema

**Generated**: {timestamp}  
**Symbol**: {symbol}  
**Pipeline Step**: Feature Engineering  
**Description**: {description}

## Overview

- **Shape**: {shape[0]:,} rows × {shape[1]} columns
- **Memory Usage**: {memory_mb:.2f} MB
- **Total Features**: {len([c for c in df.columns if c not in ['trading_date_local', 'symbol', 'target']])}
- **Technical Indicators**: {len([c for c in df.columns if any(x in c.lower() for x in ['rsi', 'macd', 'sma', 'ema', 'bollinger'])])}

## Column Details

| Column | Data Type | Null Count | Null % | Notes |
|--------|-----------|------------|--------|-------|
"""
        
        for col_info in columns_info:
            md_content += f"| {col_info['column']} | {col_info['dtype']} | {col_info['null_count']} | {col_info['null_pct']:.1f}% | {col_info['sample_values']} |\n"
        
        # Add key numeric columns summary
        if key_numeric_cols:
            md_content += f"\n## Key Feature Statistics\n\n"
            for col in key_numeric_cols:
                if col in df.columns:
                    stats = df[col].describe()
                    md_content += f"### {col}\n"
                    md_content += f"- **Mean**: {stats['mean']:.4f}\n"
                    md_content += f"- **Std**: {stats['std']:.4f}\n"
                    md_content += f"- **Min**: {stats['min']:.4f}\n"
                    md_content += f"- **Max**: {stats['max']:.4f}\n\n"
        
        # Add sample data
        md_content += "\n## Sample Data (First 3 Rows)\n\n"
        if len(df) >= 3:
            sample_df = df.head(3)
            md_content += sample_df.to_markdown(index=False, floatfmt=".4f")
        
        # Database integration notes
        md_content += f"\n\n## Database Integration Notes\n\n"
        md_content += "### Key Features for Database Storage\n"
        
        # Categorize features
        price_features = [c for c in df.columns if 'price' in c.lower()]
        technical_indicators = [c for c in df.columns if any(x in c.lower() for x in ['rsi', 'macd', 'sma', 'ema', 'bollinger', 'stoch', 'williams', 'atr', 'adx'])]
        volume_features = [c for c in df.columns if 'volume' in c.lower()]
        growth_features = [c for c in df.columns if 'growth' in c.lower()]
        target_features = [c for c in df.columns if 'target' in c.lower()]
        
        if price_features:
            md_content += f"- **Price Features** ({len(price_features)}): {', '.join(price_features[:5])}\n"
        if technical_indicators:
            md_content += f"- **Technical Indicators** ({len(technical_indicators)}): {', '.join(technical_indicators[:10])}\n"
        if volume_features:
            md_content += f"- **Volume Features** ({len(volume_features)}): {', '.join(volume_features)}\n"
        if growth_features:
            md_content += f"- **Growth Features** ({len(growth_features)}): {', '.join(growth_features[:5])}\n"
        if target_features:
            md_content += f"- **Target Variables** ({len(target_features)}): {', '.join(target_features)}\n"
        
        # Save to file
        filename = f"{name}_{symbol.lower()}.md"
        file_path = docs_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        print(f"📋 Documented {name} DataFrame: {file_path}")
        
    except Exception as e:
        print(f"❌ Failed to document DataFrame {name}: {e}")

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
        
    def create_target_variable(self, df: pd.DataFrame, target_days: int = 7) -> pd.DataFrame:
        """
        Create target variable for future growth prediction
        
        Args:
            df: Stock DataFrame with close_price column
            target_days: Number of days to look ahead (default: 7 for weekly prediction)
            
        Returns:
            DataFrame with target variable added
        """
        df = df.copy()
        
        # 7-day forward growth rate (more predictable than 30-day)
        df[f'growth_future_{target_days}d'] = df['close_price'].shift(-target_days) / df['close_price']
        
        # Binary target: 1 if positive growth, 0 otherwise
        df['target'] = (df[f'growth_future_{target_days}d'] > 1).astype(int)
        
        # Remove last N rows (no future data available)
        df = df.iloc[:-target_days].copy()
        
        target_distribution = df['target'].value_counts(normalize=True)
        logger.info(f"Target distribution ({target_days}-day growth) - Positive: {target_distribution.get(1, 0):.2%}, Negative: {target_distribution.get(0, 0):.2%}")
        
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
    
    def create_logarithmic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate logarithmic transformations for financial stability"""
        df = df.copy()
        
        # Log returns (more stable than simple returns)
        df['log_return_1d'] = np.log(df['close_price'] / df['close_price'].shift(1))
        df['log_return_5d'] = np.log(df['close_price'] / df['close_price'].shift(5))
        df['log_return_20d'] = np.log(df['close_price'] / df['close_price'].shift(20))
        df['log_return_60d'] = np.log(df['close_price'] / df['close_price'].shift(60))
        
        # Cumulative log returns (trend strength)
        df['cum_log_return_30d'] = df['log_return_1d'].rolling(30).sum()
        df['cum_log_return_60d'] = df['log_return_1d'].rolling(60).sum()
        df['cum_log_return_180d'] = df['log_return_1d'].rolling(180).sum()
        
        # Log volatility (stabilize variance)
        df['log_volatility_20d'] = np.log(df['volatility_20d'] + 1e-8)
        df['log_volatility_60d'] = np.log(df['volatility_60d'] + 1e-8)
        
        # Log volume features (handle volume spikes)
        df['log_volume'] = np.log(df['volume'] + 1)
        df['log_volume_ma_20'] = np.log(df['volume_ma_20'] + 1)
        df['log_volume_ratio_20d'] = np.log(df['volume_ratio_20d'] + 1e-8)
        
        # Log price ratios (relative value analysis)
        df['log_price_to_sma_20'] = np.log(df['close_price'] / df['sma_20'])
        df['log_price_to_sma_50'] = np.log(df['close_price'] / df['sma_50'])
        df['log_price_to_sma_200'] = np.log(df['close_price'] / df['sma_200'])
        
        # Log of Bollinger Band features
        df['log_bb_width'] = np.log(df['bb_width'] + 1e-8)
        df['log_bb_position'] = np.log(df['bb_position'] + 1e-8)
        
        # Box-Cox transformations for highly skewed data
        try:
            # Only apply if we have positive values
            positive_volume = df['volume'] + 1
            df['volume_boxcox'], _ = boxcox(positive_volume)
            
            positive_momentum = np.abs(df['price_momentum_20d']) + 1
            df['price_momentum_boxcox'], _ = boxcox(positive_momentum)
        except Exception:
            logger.warning("Box-Cox transformation failed, using log fallback")
            df['volume_boxcox'] = np.log(df['volume'] + 1)
            df['price_momentum_boxcox'] = np.log(np.abs(df['price_momentum_20d']) + 1)
        
        # Log-odds transformations for bounded indicators
        df['rsi_log_odds'] = np.log((df['rsi_14'] + 1e-8) / (100 - df['rsi_14'] + 1e-8))
        df['stoch_k_log_odds'] = np.log((df['stoch_k'] + 1e-8) / (100 - df['stoch_k'] + 1e-8))
        
        # Sigmoid transformations for unbounded indicators
        df['macd_sigmoid'] = 1 / (1 + np.exp(-df['macd']))
        df['williams_r_sigmoid'] = 1 / (1 + np.exp(-df['williams_r'] / 10))
        
        logarithmic_features = ['log_return_1d', 'log_return_5d', 'log_return_20d', 'log_return_60d',
                               'cum_log_return_30d', 'cum_log_return_60d', 'cum_log_return_180d',
                               'log_volatility_20d', 'log_volatility_60d', 'log_volume', 'log_volume_ma_20',
                               'log_volume_ratio_20d', 'log_price_to_sma_20', 'log_price_to_sma_50',
                               'log_price_to_sma_200', 'log_bb_width', 'log_bb_position',
                               'volume_boxcox', 'price_momentum_boxcox', 'rsi_log_odds', 'stoch_k_log_odds',
                               'macd_sigmoid', 'williams_r_sigmoid']
        
        logger.debug(f"Created {len(logarithmic_features)} logarithmic features")
        return df
    
    def create_spectral_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate Fourier transform and spectral analysis features"""
        df = df.copy()
        
        def compute_fft_features(price_series, window=60):
            """Compute Fast Fourier Transform features for price series"""
            if len(price_series) < window or price_series.isna().any():
                return {
                    'fft_dominant_power_1': np.nan,
                    'fft_dominant_power_2': np.nan,
                    'fft_dominant_freq_1': np.nan,
                    'fft_spectral_centroid': np.nan,
                    'fft_spectral_rolloff': np.nan,
                    'fft_spectral_bandwidth': np.nan
                }
            
            # Apply window to reduce spectral leakage
            windowed_data = price_series.values * np.hanning(len(price_series.values))
            fft_vals = np.fft.fft(windowed_data)
            power_spectrum = np.abs(fft_vals[:len(fft_vals)//2])
            
            if len(power_spectrum) == 0 or np.sum(power_spectrum) == 0:
                return {
                    'fft_dominant_power_1': 0,
                    'fft_dominant_power_2': 0,
                    'fft_dominant_freq_1': 0,
                    'fft_spectral_centroid': 0,
                    'fft_spectral_rolloff': 0,
                    'fft_spectral_bandwidth': 0
                }
            
            # Extract dominant frequencies
            dominant_freq_idx = np.argsort(power_spectrum)[-3:]
            
            # Spectral centroid (brightness measure)
            spectral_centroid = np.sum(np.arange(len(power_spectrum)) * power_spectrum) / np.sum(power_spectrum)
            
            # Spectral rolloff (90% of energy point)
            cumsum = np.cumsum(power_spectrum)
            rolloff_idx = np.where(cumsum >= 0.9 * cumsum[-1])[0]
            spectral_rolloff = rolloff_idx[0] / len(power_spectrum) if len(rolloff_idx) > 0 else 1.0
            
            # Spectral bandwidth (spread around centroid)
            spectral_bandwidth = np.sqrt(np.sum(((np.arange(len(power_spectrum)) - spectral_centroid) ** 2) * power_spectrum) / np.sum(power_spectrum))
            
            return {
                'fft_dominant_power_1': power_spectrum[dominant_freq_idx[-1]] if len(dominant_freq_idx) > 0 else 0,
                'fft_dominant_power_2': power_spectrum[dominant_freq_idx[-2]] if len(dominant_freq_idx) > 1 else 0,
                'fft_dominant_freq_1': dominant_freq_idx[-1] / len(price_series) if len(dominant_freq_idx) > 0 else 0,
                'fft_spectral_centroid': spectral_centroid / len(power_spectrum),
                'fft_spectral_rolloff': spectral_rolloff,
                'fft_spectral_bandwidth': spectral_bandwidth / len(power_spectrum)
            }
        
        def compute_dct_features(price_series, n_components=5):
            """Compute Discrete Cosine Transform features"""
            if len(price_series) < n_components or price_series.isna().any():
                return {
                    'dct_trend_strength': np.nan,
                    'dct_price_vs_trend': np.nan,
                    'dct_trend_slope': np.nan
                }
            
            try:
                dct_coeffs = dct(price_series.values, type=2, norm='ortho')
                
                # Reconstruct with only low-frequency components (trend)
                dct_coeffs_filtered = np.zeros_like(dct_coeffs)
                dct_coeffs_filtered[:n_components] = dct_coeffs[:n_components]
                trend = idct(dct_coeffs_filtered, type=2, norm='ortho')
                
                # Trend strength (low freq energy / total energy)
                trend_strength = np.sum(dct_coeffs[:n_components]**2) / (np.sum(dct_coeffs**2) + 1e-8)
                
                # Price deviation from trend
                price_vs_trend = price_series.iloc[-1] - trend[-1]
                
                # Trend slope (change over last 10 points)
                trend_slope = (trend[-1] - trend[-10]) / 10 if len(trend) >= 10 else 0
                
                return {
                    'dct_trend_strength': trend_strength,
                    'dct_price_vs_trend': price_vs_trend,
                    'dct_trend_slope': trend_slope
                }
            except Exception:
                return {
                    'dct_trend_strength': 0,
                    'dct_price_vs_trend': 0,
                    'dct_trend_slope': 0
                }
        
        def compute_wavelet_features(price_series, scales=[2, 4, 8, 16]):
            """Compute Continuous Wavelet Transform features"""
            if len(price_series) < max(scales) or price_series.isna().any():
                return {f'wavelet_energy_scale_{scale}': np.nan for scale in scales}
            
            try:
                cwt_matrix = signal.cwt(price_series.values, signal.ricker, scales)
                
                features = {}
                for i, scale in enumerate(scales):
                    if i < len(cwt_matrix):
                        features[f'wavelet_energy_scale_{scale}'] = np.sum(cwt_matrix[i]**2)
                    else:
                        features[f'wavelet_energy_scale_{scale}'] = 0
                
                # Total energy and entropy
                total_energy = np.sum(cwt_matrix**2)
                features['wavelet_total_energy'] = total_energy
                
                # Wavelet entropy
                if total_energy > 0:
                    energy_dist = cwt_matrix**2 / total_energy
                    entropy = -np.sum(energy_dist * np.log(energy_dist + 1e-8))
                    features['wavelet_entropy'] = entropy
                else:
                    features['wavelet_entropy'] = 0
                
                return features
            except Exception:
                return {f'wavelet_energy_scale_{scale}': 0 for scale in scales}
        
        # Apply spectral analysis with rolling windows
        window_sizes = [60, 120]  # Different time scales
        
        for window in window_sizes:
            # Initialize columns
            fft_cols = [f'fft_dominant_power_1_{window}', f'fft_dominant_power_2_{window}', 
                       f'fft_dominant_freq_1_{window}', f'fft_spectral_centroid_{window}',
                       f'fft_spectral_rolloff_{window}', f'fft_spectral_bandwidth_{window}']
            
            dct_cols = [f'dct_trend_strength_{window}', f'dct_price_vs_trend_{window}', 
                       f'dct_trend_slope_{window}']
            
            wavelet_cols = [f'wavelet_energy_scale_2_{window}', f'wavelet_energy_scale_4_{window}',
                           f'wavelet_energy_scale_8_{window}', f'wavelet_energy_scale_16_{window}',
                           f'wavelet_total_energy_{window}', f'wavelet_entropy_{window}']
            
            # Initialize all columns with NaN
            for col in fft_cols + dct_cols + wavelet_cols:
                df[col] = np.nan
            
            # Compute features for sufficient data points
            for i in range(window, len(df)):
                price_window = df['close_price'].iloc[i-window:i]
                
                # FFT features
                fft_features = compute_fft_features(price_window, window)
                for j, col in enumerate(fft_cols):
                    feature_key = list(fft_features.keys())[j]
                    df.loc[df.index[i], col] = fft_features[feature_key]
                
                # DCT features
                dct_features = compute_dct_features(price_window)
                for j, col in enumerate(dct_cols):
                    feature_key = list(dct_features.keys())[j]
                    df.loc[df.index[i], col] = dct_features[feature_key]
                
                # Wavelet features
                wavelet_features = compute_wavelet_features(price_window)
                for col in wavelet_cols:
                    if col.endswith(f'_{window}'):
                        base_key = col.replace(f'_{window}', '')
                        if base_key in wavelet_features:
                            df.loc[df.index[i], col] = wavelet_features[base_key]
        
        spectral_features = [col for col in df.columns if any(x in col for x in ['fft_', 'dct_', 'wavelet_'])]
        
        logger.debug(f"Created {len(spectral_features)} spectral analysis features")
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
        
    def create_chaos_theory_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate chaos theory and nonlinear dynamics features"""
        df = df.copy()
        close = df['close_price'].values
        
        try:
            # Lyapunov exponent approximation (measure of chaos/sensitivity)
            def lyapunov_exponent(series, lag=1, window=30):
                """Approximate Lyapunov exponent for chaos detection"""
                result = np.full(len(series), np.nan)
                for i in range(window, len(series)):
                    segment = series[i-window:i]
                    if len(np.unique(segment)) < 3:  # Avoid constant segments
                        continue
                    
                    # Calculate divergence rates
                    divergences = []
                    for j in range(1, min(10, len(segment)-lag)):
                        if abs(segment[j] - segment[j-lag]) > 1e-10:
                            div = abs(segment[j+lag] - segment[j]) / abs(segment[j] - segment[j-lag])
                            if div > 0:
                                divergences.append(np.log(div))
                    
                    if divergences:
                        result[i] = np.mean(divergences)
                return result
            
            df['lyapunov_exponent'] = lyapunov_exponent(close)
            
            # Hurst exponent (measure of long-term memory and self-similarity)
            def hurst_exponent(series, window=50):
                """Calculate rolling Hurst exponent"""
                result = np.full(len(series), np.nan)
                for i in range(window, len(series)):
                    segment = series[i-window:i]
                    if len(np.unique(segment)) < 3:
                        continue
                    
                    # R/S analysis
                    lags = np.arange(2, min(20, len(segment)//2))
                    rs_values = []
                    
                    for lag in lags:
                        if lag >= len(segment):
                            continue
                        
                        # Calculate R/S for this lag
                        segments = [segment[j:j+lag] for j in range(0, len(segment)-lag+1, lag)]
                        rs_lag = []
                        
                        for seg in segments:
                            if len(seg) == lag and len(np.unique(seg)) > 1:
                                mean_seg = np.mean(seg)
                                dev = seg - mean_seg
                                cum_dev = np.cumsum(dev)
                                R = np.max(cum_dev) - np.min(cum_dev)
                                S = np.std(seg)
                                if S > 0:
                                    rs_lag.append(R/S)
                        
                        if rs_lag:
                            rs_values.append(np.mean(rs_lag))
                    
                    if len(rs_values) >= 3:
                        # Linear regression of log(R/S) vs log(n)
                        log_lags = np.log(lags[:len(rs_values)])
                        log_rs = np.log(rs_values)
                        
                        # Remove infinite/NaN values
                        valid_mask = np.isfinite(log_lags) & np.isfinite(log_rs)
                        if np.sum(valid_mask) >= 3:
                            hurst = np.polyfit(log_lags[valid_mask], log_rs[valid_mask], 1)[0]
                            result[i] = np.clip(hurst, 0, 1)  # Hurst should be between 0 and 1
                
                return result
            
            df['hurst_exponent'] = hurst_exponent(close)
            
            # Fractal dimension (measure of complexity)
            def fractal_dimension(series, window=30):
                """Box-counting fractal dimension approximation"""
                result = np.full(len(series), np.nan)
                for i in range(window, len(series)):
                    segment = series[i-window:i]
                    if len(np.unique(segment)) < 3:
                        continue
                    
                    # Normalize segment
                    normalized = (segment - np.min(segment)) / (np.max(segment) - np.min(segment) + 1e-10)
                    
                    # Box counting with different scales
                    scales = [2, 4, 8, 16]
                    counts = []
                    
                    for scale in scales:
                        if scale >= len(normalized):
                            continue
                        
                        # Count boxes containing data
                        box_size = 1.0 / scale
                        boxes = set()
                        for j, val in enumerate(normalized):
                            box_x = j // (len(normalized) // scale)
                            box_y = int(val / box_size)
                            boxes.add((box_x, box_y))
                        counts.append(len(boxes))
                    
                    if len(counts) >= 3:
                        log_scales = np.log([1.0/s for s in scales[:len(counts)]])
                        log_counts = np.log(counts)
                        
                        valid_mask = np.isfinite(log_scales) & np.isfinite(log_counts)
                        if np.sum(valid_mask) >= 3:
                            fd = -np.polyfit(log_scales[valid_mask], log_counts[valid_mask], 1)[0]
                            result[i] = np.clip(fd, 1, 2)  # Fractal dimension should be between 1 and 2
                
                return result
            
            df['fractal_dimension'] = fractal_dimension(close)
            
            # Entropy measures
            def sample_entropy(series, window=30, m=2, r_factor=0.2):
                """Calculate sample entropy (measure of regularity)"""
                result = np.full(len(series), np.nan)
                for i in range(window, len(series)):
                    segment = series[i-window:i]
                    if len(segment) < m + 1:
                        continue
                    
                    # Calculate relative tolerance
                    r = r_factor * np.std(segment)
                    if r <= 0:
                        continue
                    
                    def _maxdist(xi, xj, m):
                        return max([abs(xi[k] - xj[k]) for k in range(m)])
                    
                    def _phi(m):
                        patterns = []
                        for j in range(len(segment) - m + 1):
                            patterns.append(segment[j:j+m])
                        
                        matches = 0
                        for j in range(len(patterns)):
                            for k in range(j+1, len(patterns)):
                                if _maxdist(patterns[j], patterns[k], m) <= r:
                                    matches += 1
                        
                        total_pairs = len(patterns) * (len(patterns) - 1) // 2
                        return matches / max(total_pairs, 1)
                    
                    phi_m = _phi(m)
                    phi_m1 = _phi(m + 1)
                    
                    if phi_m > 0 and phi_m1 > 0:
                        sample_ent = -np.log(phi_m1 / phi_m)
                        result[i] = sample_ent
                
                return result
            
            df['sample_entropy'] = sample_entropy(close)
            
            # Chaos indicators based on phase space reconstruction
            def recurrence_quantification(series, window=40):
                """Recurrence rate as chaos indicator"""
                result = np.full(len(series), np.nan)
                for i in range(window, len(series)):
                    segment = series[i-window:i]
                    
                    # Phase space reconstruction (embedding dimension = 2)
                    embedded = np.array([[segment[j], segment[j+1]] for j in range(len(segment)-1)])
                    
                    if len(embedded) < 10:
                        continue
                    
                    # Calculate recurrence matrix
                    threshold = 0.1 * np.std(segment)
                    recurrences = 0
                    total_pairs = 0
                    
                    for j in range(len(embedded)):
                        for k in range(j+1, len(embedded)):
                            distance = np.linalg.norm(embedded[j] - embedded[k])
                            if distance <= threshold:
                                recurrences += 1
                            total_pairs += 1
                    
                    if total_pairs > 0:
                        recurrence_rate = recurrences / total_pairs
                        result[i] = recurrence_rate
                
                return result
            
            df['recurrence_rate'] = recurrence_quantification(close)
            
            chaos_features = ['lyapunov_exponent', 'hurst_exponent', 'fractal_dimension', 
                            'sample_entropy', 'recurrence_rate']
            
        except Exception as e:
            logger.warning(f"Error creating chaos theory features: {e}")
            # Create placeholder columns
            chaos_features = ['lyapunov_exponent', 'hurst_exponent', 'fractal_dimension', 
                            'sample_entropy', 'recurrence_rate']
            for feature in chaos_features:
                df[feature] = np.nan
        
        logger.debug(f"Created {len(chaos_features)} chaos theory features")
        return df
    
    def create_thermodynamics_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate thermodynamics-inspired features for market dynamics"""
        df = df.copy()
        close = df['close_price'].values
        volume = df['volume'].values
        
        try:
            # Market temperature (volatility as thermal energy)
            def market_temperature(prices, window=20):
                """Market temperature based on price volatility"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    # Temperature as normalized variance
                    temp = np.var(segment) / (np.mean(segment)**2 + 1e-10)
                    result[i] = temp
                return result
            
            df['market_temperature'] = market_temperature(close)
            
            # Market entropy (information content)
            def market_entropy(prices, volumes, window=30):
                """Market entropy based on price-volume distribution"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    price_segment = prices[i-window:i]
                    volume_segment = volumes[i-window:i]
                    
                    # Discretize price changes
                    price_changes = np.diff(price_segment)
                    if len(price_changes) == 0 or np.std(price_changes) == 0:
                        continue
                    
                    # Create bins based on standard deviation
                    std_change = np.std(price_changes)
                    bins = [-3*std_change, -std_change, 0, std_change, 3*std_change]
                    
                    # Weight by volume
                    weights = volume_segment[1:]  # Match length with price_changes
                    weights = weights / np.sum(weights)  # Normalize
                    
                    # Calculate weighted entropy
                    hist, _ = np.histogram(price_changes, bins=bins, weights=weights)
                    hist = hist / np.sum(hist)  # Normalize probabilities
                    
                    # Shannon entropy
                    entropy = -np.sum(hist * np.log(hist + 1e-10))
                    result[i] = entropy
                
                return result
            
            df['market_entropy'] = market_entropy(close, volume)
            
            # Free energy (trend strength vs randomness)
            def free_energy(prices, window=25):
                """Free energy as trend strength minus entropy"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    
                    # Trend strength (internal energy)
                    returns = np.diff(segment) / segment[:-1]
                    trend_strength = abs(np.mean(returns)) * window  # Amplify signal
                    
                    # Randomness (entropy term)
                    if np.std(returns) > 0:
                        normalized_returns = (returns - np.mean(returns)) / np.std(returns)
                        # Histogram entropy
                        hist, _ = np.histogram(normalized_returns, bins=10)
                        hist = hist / np.sum(hist)
                        entropy = -np.sum(hist * np.log(hist + 1e-10))
                        
                        # Free energy = internal energy - temperature * entropy
                        # Use volatility as temperature
                        temperature = np.std(returns)
                        free_energy_val = trend_strength - temperature * entropy
                        result[i] = free_energy_val
                
                return result
            
            df['free_energy'] = free_energy(close)
            
            # Heat capacity (response to price shocks)
            def heat_capacity(prices, window=20):
                """Heat capacity as sensitivity to price changes"""
                result = np.full(len(prices), np.nan)
                for i in range(window*2, len(prices)):
                    # Compare volatility before and after price shocks
                    segment = prices[i-window*2:i]
                    mid_point = len(segment) // 2
                    
                    vol_before = np.std(segment[:mid_point])
                    vol_after = np.std(segment[mid_point:])
                    
                    # Heat capacity as change in volatility response
                    if vol_before > 0:
                        heat_cap = (vol_after - vol_before) / vol_before
                        result[i] = heat_cap
                
                return result
            
            df['heat_capacity'] = heat_capacity(close)
            
            # Phase transition indicator (regime change detection)
            def phase_transition(prices, window=40):
                """Detect phase transitions in market regimes"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    
                    # Calculate order parameter (trend consistency)
                    returns = np.diff(segment) / segment[:-1]
                    
                    # Moving correlation as order parameter
                    half_window = len(returns) // 2
                    if half_window < 3:
                        continue
                        
                    early_returns = returns[:half_window]
                    late_returns = returns[-half_window:]
                    
                    # Correlation between early and late periods
                    if len(early_returns) > 0 and len(late_returns) > 0:
                        # Autocorrelation as order parameter
                        corr1 = np.corrcoef(early_returns[:-1], early_returns[1:])[0,1]
                        corr2 = np.corrcoef(late_returns[:-1], late_returns[1:])[0,1]
                        
                        if not (np.isnan(corr1) or np.isnan(corr2)):
                            # Phase transition as change in order
                            phase_change = abs(corr2 - corr1)
                            result[i] = phase_change
                
                return result
            
            df['phase_transition'] = phase_transition(close)
            
            thermo_features = ['market_temperature', 'market_entropy', 'free_energy', 
                             'heat_capacity', 'phase_transition']
            
        except Exception as e:
            logger.warning(f"Error creating thermodynamics features: {e}")
            # Create placeholder columns
            thermo_features = ['market_temperature', 'market_entropy', 'free_energy', 
                             'heat_capacity', 'phase_transition']
            for feature in thermo_features:
                df[feature] = np.nan
        
        logger.debug(f"Created {len(thermo_features)} thermodynamics features")
        return df
    
    def create_wave_physics_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate wave physics and electromagnetic features"""
        df = df.copy()
        close = df['close_price'].values
        volume = df['volume'].values
        
        try:
            # Wave interference patterns
            def wave_interference(prices, window=50):
                """Wave interference using multiple frequency components"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    
                    # Detrend for wave analysis
                    detrended = segment - np.linspace(segment[0], segment[-1], len(segment))
                    
                    # Create multiple wave components
                    t = np.arange(len(detrended))
                    
                    # Primary wave (dominant frequency from autocorrelation)
                    autocorr = np.correlate(detrended, detrended, mode='full')
                    autocorr = autocorr[len(autocorr)//2:]
                    
                    if len(autocorr) > 10:
                        # Find dominant period
                        peaks = []
                        for j in range(2, min(len(autocorr)//2, 25)):
                            if autocorr[j] > autocorr[j-1] and autocorr[j] > autocorr[j+1]:
                                peaks.append((j, autocorr[j]))
                        
                        if peaks:
                            dominant_period = max(peaks, key=lambda x: x[1])[0]
                            
                            # Primary wave
                            wave1 = np.sin(2 * np.pi * t / dominant_period)
                            
                            # Harmonic waves
                            wave2 = np.sin(2 * np.pi * t / (dominant_period / 2))
                            wave3 = np.sin(2 * np.pi * t / (dominant_period * 2))
                            
                            # Wave interference (superposition)
                            interference = wave1 + 0.5 * wave2 + 0.3 * wave3
                            
                            # Correlation with actual price movement
                            correlation = np.corrcoef(detrended, interference)[0, 1]
                            if not np.isnan(correlation):
                                result[i] = correlation
                
                return result
            
            df['wave_interference'] = wave_interference(close)
            
            # Standing wave patterns
            def standing_waves(prices, window=40):
                """Detect standing wave patterns in price movements"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    
                    # Find nodes (points of minimal movement)
                    returns = np.abs(np.diff(segment))
                    
                    # Smooth to find nodes
                    smoothed_returns = np.convolve(returns, np.ones(5)/5, mode='same')
                    
                    # Find local minima (nodes)
                    nodes = []
                    for j in range(2, len(smoothed_returns)-2):
                        if (smoothed_returns[j] < smoothed_returns[j-1] and 
                            smoothed_returns[j] < smoothed_returns[j+1]):
                            nodes.append(j)
                    
                    if len(nodes) >= 3:
                        # Calculate node spacing regularity
                        node_spacings = np.diff(nodes)
                        if len(node_spacings) > 1:
                            spacing_std = np.std(node_spacings) / (np.mean(node_spacings) + 1e-10)
                            # Lower std = more regular standing wave
                            standing_wave_strength = 1.0 / (1.0 + spacing_std)
                            result[i] = standing_wave_strength
                
                return result
            
            df['standing_waves'] = standing_waves(close)
            
            # Electromagnetic field analogies
            def electric_field(prices, window=30):
                """Price gradient as electric field strength"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    
                    # Electric field as price gradient
                    gradient = np.gradient(segment)
                    
                    # Field strength (magnitude of gradient)
                    field_strength = np.sqrt(np.mean(gradient**2))
                    result[i] = field_strength
                
                return result
            
            df['electric_field'] = electric_field(close)
            
            def magnetic_field(prices, volumes, window=25):
                """Volume-price curl as magnetic field"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    price_segment = prices[i-window:i]
                    volume_segment = volumes[i-window:i]
                    
                    if np.std(volume_segment) > 0:
                        # Normalize volume
                        norm_volume = (volume_segment - np.mean(volume_segment)) / np.std(volume_segment)
                        
                        # Price momentum
                        price_momentum = np.gradient(price_segment)
                        
                        # Cross product analogy (curl)
                        # Magnetic field strength from volume-momentum interaction
                        magnetic_strength = np.mean(np.abs(norm_volume[1:] * price_momentum[1:]))
                        result[i] = magnetic_strength
                
                return result
            
            df['magnetic_field'] = magnetic_field(close, volume)
            
            # Wave dispersion (frequency-dependent wave speed)
            def wave_dispersion(prices, window=60):
                """Measure wave dispersion in price movements"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    
                    # FFT to get frequency components
                    fft_values = np.fft.fft(segment - np.mean(segment))
                    frequencies = np.fft.fftfreq(len(segment))
                    
                    # Power spectrum
                    power_spectrum = np.abs(fft_values)**2
                    
                    # Positive frequencies only
                    pos_freq_mask = frequencies > 0
                    pos_frequencies = frequencies[pos_freq_mask]
                    pos_power = power_spectrum[pos_freq_mask]
                    
                    if len(pos_frequencies) > 5:
                        # Group velocity dispersion
                        # Higher frequencies should travel faster in trending markets
                        freq_bins = [0.1, 0.2, 0.3, 0.4, 0.5]
                        bin_powers = []
                        
                        for j in range(len(freq_bins)-1):
                            mask = (pos_frequencies >= freq_bins[j]) & (pos_frequencies < freq_bins[j+1])
                            if np.sum(mask) > 0:
                                bin_powers.append(np.mean(pos_power[mask]))
                            else:
                                bin_powers.append(0)
                        
                        # Dispersion as power distribution across frequencies
                        if len(bin_powers) > 1 and sum(bin_powers) > 0:
                            bin_powers = np.array(bin_powers) / sum(bin_powers)
                            # Shannon entropy of power distribution
                            dispersion = -np.sum(bin_powers * np.log(bin_powers + 1e-10))
                            result[i] = dispersion
                
                return result
            
            df['wave_dispersion'] = wave_dispersion(close)
            
            # Resonance detection
            def resonance_frequency(prices, volumes, window=45):
                """Detect price-volume resonance frequencies"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    price_segment = prices[i-window:i]
                    volume_segment = volumes[i-window:i]
                    
                    # Detrend both signals
                    price_detrended = price_segment - np.linspace(price_segment[0], price_segment[-1], len(price_segment))
                    volume_detrended = volume_segment - np.linspace(volume_segment[0], volume_segment[-1], len(volume_segment))
                    
                    if np.std(price_detrended) > 0 and np.std(volume_detrended) > 0:
                        # Cross-correlation to find phase relationships
                        xcorr = np.correlate(price_detrended, volume_detrended, mode='full')
                        
                        # Find peak correlation (resonance)
                        max_corr_idx = np.argmax(np.abs(xcorr))
                        max_correlation = xcorr[max_corr_idx]
                        
                        # Phase delay
                        phase_delay = max_corr_idx - len(price_detrended) + 1
                        
                        # Resonance strength (normalized correlation)
                        resonance_strength = abs(max_correlation) / (len(price_detrended) * np.std(price_detrended) * np.std(volume_detrended))
                        result[i] = resonance_strength
                
                return result
            
            df['resonance_frequency'] = resonance_frequency(close, volume)
            
            wave_features = ['wave_interference', 'standing_waves', 'electric_field', 
                           'magnetic_field', 'wave_dispersion', 'resonance_frequency']
            
        except Exception as e:
            logger.warning(f"Error creating wave physics features: {e}")
            # Create placeholder columns
            wave_features = ['wave_interference', 'standing_waves', 'electric_field', 
                           'magnetic_field', 'wave_dispersion', 'resonance_frequency']
            for feature in wave_features:
                df[feature] = np.nan
        
        logger.debug(f"Created {len(wave_features)} wave physics features")
        return df
    
    def create_brownian_motion_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate Brownian motion and statistical physics features"""
        df = df.copy()
        close = df['close_price'].values
        volume = df['volume'].values
        
        try:
            # Random walk characteristics
            def random_walk_analysis(prices, window=50):
                """Analyze random walk properties"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    returns = np.diff(np.log(segment))
                    
                    if np.std(returns) > 0:
                        # Variance ratio test for random walk
                        # Compare variance of k-period returns to k * variance of 1-period returns
                        k_values = [2, 4, 8]
                        variance_ratios = []
                        
                        one_period_var = np.var(returns)
                        
                        for k in k_values:
                            if k < len(returns):
                                k_period_returns = []
                                for j in range(0, len(returns) - k + 1, k):
                                    k_period_returns.append(np.sum(returns[j:j+k]))
                                
                                if len(k_period_returns) > 1:
                                    k_period_var = np.var(k_period_returns)
                                    if one_period_var > 0:
                                        variance_ratio = k_period_var / (k * one_period_var)
                                        variance_ratios.append(variance_ratio)
                        
                        if variance_ratios:
                            # Mean variance ratio (should be ~1 for true random walk)
                            mean_vr = np.mean(variance_ratios)
                            # Deviation from random walk
                            rw_deviation = abs(mean_vr - 1.0)
                            result[i] = rw_deviation
                
                return result
            
            df['random_walk_deviation'] = random_walk_analysis(close)
            
            # Diffusion coefficient
            def diffusion_coefficient(prices, window=40):
                """Calculate diffusion coefficient for Brownian motion"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    log_prices = np.log(segment)
                    
                    # Mean squared displacement
                    displacements = []
                    for lag in range(1, min(10, len(log_prices)//2)):
                        for j in range(len(log_prices) - lag):
                            displacement = (log_prices[j + lag] - log_prices[j])**2
                            displacements.append((lag, displacement))
                    
                    if len(displacements) > 10:
                        # Group by lag and calculate mean squared displacement
                        lag_dict = {}
                        for lag, disp in displacements:
                            if lag not in lag_dict:
                                lag_dict[lag] = []
                            lag_dict[lag].append(disp)
                        
                        msd_values = []
                        lag_values = []
                        for lag, disps in lag_dict.items():
                            msd_values.append(np.mean(disps))
                            lag_values.append(lag)
                        
                        if len(msd_values) >= 3:
                            # Linear regression: MSD = 2 * D * t (for Brownian motion)
                            # D is the diffusion coefficient
                            slope = np.polyfit(lag_values, msd_values, 1)[0]
                            diffusion_coeff = slope / 2.0
                            result[i] = abs(diffusion_coeff)
                
                return result
            
            df['diffusion_coefficient'] = diffusion_coefficient(close)
            
            # Ornstein-Uhlenbeck process characteristics (mean reversion)
            def ou_process_analysis(prices, window=60):
                """Analyze Ornstein-Uhlenbeck mean reversion properties"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    log_prices = np.log(segment)
                    
                    # Fit OU process: dx = theta * (mu - x) * dt + sigma * dW
                    # Discrete approximation: x[t+1] - x[t] = alpha + beta * x[t] + noise
                    # where beta = -theta * dt, alpha = theta * mu * dt
                    
                    if len(log_prices) >= 10:
                        x = log_prices[:-1]  # x[t]
                        dx = np.diff(log_prices)  # x[t+1] - x[t]
                        
                        # Linear regression: dx = alpha + beta * x
                        if np.std(x) > 0:
                            coeffs = np.polyfit(x, dx, 1)
                            beta, alpha = coeffs
                            
                            # Mean reversion speed (should be negative for mean reversion)
                            theta = -beta
                            
                            # Long-term mean
                            if theta != 0:
                                mu = alpha / theta
                                
                                # Mean reversion strength
                                mean_reversion_strength = abs(theta)
                                result[i] = mean_reversion_strength
                
                return result
            
            df['ou_mean_reversion'] = ou_process_analysis(close)
            
            # Jump diffusion detection
            def jump_diffusion(prices, window=35, threshold_factor=3.0):
                """Detect jump diffusion components"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    returns = np.diff(np.log(segment))
                    
                    if np.std(returns) > 0:
                        # Identify jumps (returns > threshold_factor * std)
                        threshold = threshold_factor * np.std(returns)
                        jumps = returns[np.abs(returns) > threshold]
                        
                        # Jump intensity (frequency)
                        jump_intensity = len(jumps) / len(returns)
                        
                        # Jump size (mean absolute jump)
                        if len(jumps) > 0:
                            mean_jump_size = np.mean(np.abs(jumps))
                            # Combined jump measure
                            jump_measure = jump_intensity * mean_jump_size
                        else:
                            jump_measure = 0.0
                        
                        result[i] = jump_measure
                
                return result
            
            df['jump_diffusion'] = jump_diffusion(close)
            
            # Levy flight characteristics (heavy tails)
            def levy_flight_analysis(prices, window=45):
                """Analyze Levy flight (heavy-tailed) characteristics"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    segment = prices[i-window:i]
                    returns = np.diff(np.log(segment))
                    
                    if len(returns) >= 20:
                        # Estimate tail exponent using Hill estimator
                        abs_returns = np.abs(returns)
                        sorted_returns = np.sort(abs_returns)
                        
                        # Use top 20% for tail analysis
                        k = max(4, len(sorted_returns) // 5)
                        top_returns = sorted_returns[-k:]
                        
                        if len(top_returns) > 3 and top_returns[-1] > 0:
                            # Hill estimator for tail index
                            log_ratios = []
                            for j in range(1, len(top_returns)):
                                if top_returns[-1] > 0:
                                    ratio = top_returns[-(j+1)] / top_returns[-1]
                                    if ratio > 0:
                                        log_ratios.append(np.log(ratio))
                            
                            if len(log_ratios) >= 3:
                                hill_estimate = -np.mean(log_ratios)
                                # Tail index (alpha): lower values indicate heavier tails
                                # For Gaussian: alpha ≈ ∞, for Levy: alpha < 2
                                tail_heaviness = max(0, 4.0 - hill_estimate)  # Higher = heavier tails
                                result[i] = tail_heaviness
                
                return result
            
            df['levy_flight_tails'] = levy_flight_analysis(close)
            
            # Statistical mechanics: Partition function analogy
            def partition_function(prices, volumes, window=30):
                """Market partition function (statistical mechanics analogy)"""
                result = np.full(len(prices), np.nan)
                for i in range(window, len(prices)):
                    price_segment = prices[i-window:i]
                    volume_segment = volumes[i-window:i]
                    
                    # Energy levels (price levels weighted by volume)
                    if np.std(volume_segment) > 0:
                        # Normalize volumes as probabilities
                        volume_probs = volume_segment / np.sum(volume_segment)
                        
                        # Energy as deviation from mean price
                        mean_price = np.mean(price_segment)
                        energies = (price_segment - mean_price) / mean_price
                        
                        # Partition function Z = sum(exp(-beta * E_i) * p_i)
                        # Use temperature = volatility
                        temperature = np.std(price_segment) / mean_price
                        beta = 1.0 / (temperature + 1e-10)  # Inverse temperature
                        
                        # Boltzmann factors weighted by volume probabilities
                        boltzmann_factors = np.exp(-beta * np.abs(energies)) * volume_probs
                        partition_z = np.sum(boltzmann_factors)
                        
                        # Free energy = -ln(Z) / beta
                        if partition_z > 0:
                            free_energy = -np.log(partition_z) / beta
                            result[i] = free_energy
                
                return result
            
            df['partition_function'] = partition_function(close, volume)
            
            brownian_features = ['random_walk_deviation', 'diffusion_coefficient', 'ou_mean_reversion',
                                'jump_diffusion', 'levy_flight_tails', 'partition_function']
            
        except Exception as e:
            logger.warning(f"Error creating Brownian motion features: {e}")
            # Create placeholder columns
            brownian_features = ['random_walk_deviation', 'diffusion_coefficient', 'ou_mean_reversion',
                                'jump_diffusion', 'levy_flight_tails', 'partition_function']
            for feature in brownian_features:
                df[feature] = np.nan
        
        logger.debug(f"Created {len(brownian_features)} Brownian motion features")
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
        df = self.create_logarithmic_features(df)  # After TA-Lib features
        df = self.create_spectral_features(df)
        df = self.create_chaos_theory_features(df)
        df = self.create_thermodynamics_features(df)
        df = self.create_wave_physics_features(df)
        df = self.create_brownian_motion_features(df)
        
        # Clean invalid values (before target creation)
        df = self.clean_invalid_values(df, symbol)
        
        # Create target variable (must be last step)
        df = self.create_target_variable(df)
        
        # Remove rows with too many NaN values
        df_clean = df.dropna(thresh=len(df.columns) * 0.7)  # Keep rows with at least 70% non-NaN values
        
        features_created = len([col for col in df_clean.columns if col not in 
                              ['symbol', 'currency', 'trading_date_local', 'close_price', 'volume',
                               'open_price', 'high_price', 'low_price', 'target', 'growth_future_7d']])
        
        logger.info(f"{symbol}: Created {features_created} features. "
                   f"Data: {original_len} -> {len(df_clean)} records after cleaning")
        
        # Document the engineered features DataFrame
        document_dataframe(
            df_clean,
            f"step02_feature_engineering_output",
            f"STEP 2 - FEATURE ENGINEERING: Complete feature engineering output with {features_created} engineered features including technical indicators (RSI, MACD, Bollinger), price patterns, volume features, and binary target variable for 7-day growth prediction (more accurate than 30-day). This DataFrame feeds into the ML preprocessing step.",
            symbol
        )
        
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
    
    def analyze_feature_significance(self, df: pd.DataFrame, symbol: str, top_n: int = 20) -> Dict:
        """
        Exploratory method to analyze feature significance for binary target discrimination.
        Uses multiple statistical methods to identify most significant variables.
        
        Args:
            df: DataFrame with engineered features and target variable
            symbol: Stock symbol for logging
            top_n: Number of top features to report
            
        Returns:
            Dictionary containing feature significance results
        """
        logger.info(f"🔍 Analyzing feature significance for {symbol}...")
        
        if 'target' not in df.columns:
            logger.error(f"❌ Target variable not found in {symbol} data")
            return {}
            
        # Exclude non-feature columns
        exclude_cols = ['symbol', 'currency', 'trading_date_local', 'close_price', 'volume',
                       'open_price', 'high_price', 'low_price', 'target', 'growth_future_7d']
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Prepare data for analysis - preserve NaN values (XGBoost handles them natively)
        analysis_df = df[feature_cols + ['target']].copy()
        
        # Only require non-NaN target values
        valid_target_mask = analysis_df['target'].notna()
        analysis_df = analysis_df[valid_target_mask]
        
        if len(analysis_df) < 50:
            logger.warning(f"⚠️  Insufficient data for {symbol}: {len(analysis_df)} records")
            return {}
            
        X = analysis_df[feature_cols]
        y = analysis_df['target']
        
        logger.info(f"   📊 Analyzing {len(feature_cols)} features on {len(analysis_df)} records")
        logger.info(f"   🎯 Target distribution: Positive {(y==1).mean():.2%}, Negative {(y==0).mean():.2%}")
        
        results = {}
        
        try:
            # 1. Point-Biserial Correlation (for binary target vs continuous features)
            logger.info(f"   🔗 Computing point-biserial correlations...")
            pb_correlations = []
            for feature in feature_cols:
                # Create mask for complete cases (both feature and target non-NaN)
                complete_mask = X[feature].notna() & y.notna()
                complete_count = complete_mask.sum()
                
                if complete_count > 20 and X[feature].nunique() > 2:  # Need sufficient complete cases
                    try:
                        feature_vals = X[feature][complete_mask]
                        target_vals = y[complete_mask]
                        
                        if feature_vals.nunique() > 2:  # Still continuous after filtering
                            corr, p_val = pointbiserialr(target_vals, feature_vals)
                            pb_correlations.append({
                                'feature': feature,
                                'correlation': abs(corr),  # Use absolute value for ranking
                                'correlation_raw': corr,
                                'p_value': p_val,
                                'complete_cases': complete_count,
                                'significance': 'High' if p_val < 0.01 else 'Medium' if p_val < 0.05 else 'Low'
                            })
                    except:
                        continue
                        
            pb_correlations = sorted(pb_correlations, key=lambda x: x['correlation'], reverse=True)
            results['point_biserial'] = pb_correlations[:top_n]
            
            # 2. F-statistic for classification (ANOVA F-test) - handle NaN per feature
            logger.info(f"   📈 Computing F-statistics...")
            f_results = []
            for feature in feature_cols:
                # Use complete cases for this feature
                complete_mask = X[feature].notna() & y.notna()
                complete_count = complete_mask.sum()
                
                if complete_count > 20:  # Need sufficient complete cases
                    try:
                        feature_vals = X[feature][complete_mask].values.reshape(-1, 1)
                        target_vals = y[complete_mask].values
                        
                        f_score, p_val = f_classif(feature_vals, target_vals)
                        if not np.isnan(f_score[0]):
                            f_results.append({
                                'feature': feature,
                                'f_score': f_score[0],
                                'p_value': p_val[0],
                                'complete_cases': complete_count,
                                'significance': 'High' if p_val[0] < 0.01 else 'Medium' if p_val[0] < 0.05 else 'Low'
                            })
                    except:
                        continue
                    
            f_results = sorted(f_results, key=lambda x: x['f_score'], reverse=True)
            results['f_statistic'] = f_results[:top_n]
            
            # 3. Mutual Information (captures non-linear relationships) - handle NaN per feature
            logger.info(f"   🔄 Computing mutual information...")
            mi_results = []
            for feature in feature_cols:
                # Use complete cases for this feature
                complete_mask = X[feature].notna() & y.notna()
                complete_count = complete_mask.sum()
                
                if complete_count > 20:  # Need sufficient complete cases
                    try:
                        feature_vals = X[feature][complete_mask].values.reshape(-1, 1)
                        target_vals = y[complete_mask].values
                        
                        mi_score = mutual_info_classif(feature_vals, target_vals, random_state=42)
                        if mi_score[0] > 0:
                            mi_results.append({
                                'feature': feature,
                                'mi_score': mi_score[0],
                                'complete_cases': complete_count,
                                'normalized_mi': mi_score[0] / np.log(2)  # Normalize by log(2) for binary classification
                            })
                    except:
                        continue
                    
            mi_results = sorted(mi_results, key=lambda x: x['mi_score'], reverse=True)
            results['mutual_information'] = mi_results[:top_n]
            
            # 4. Mean difference between classes (effect size)
            logger.info(f"   📊 Computing class mean differences...")
            mean_diff_results = []
            pos_samples = analysis_df[y == 1]
            neg_samples = analysis_df[y == 0]
            
            for feature in feature_cols:
                if X[feature].nunique() > 2:  # Only for continuous features
                    try:
                        pos_mean = pos_samples[feature].mean()
                        neg_mean = neg_samples[feature].mean()
                        pooled_std = np.sqrt(((pos_samples[feature].var() * len(pos_samples) + 
                                             neg_samples[feature].var() * len(neg_samples)) / 
                                            (len(pos_samples) + len(neg_samples))))
                        
                        if pooled_std > 0:
                            cohen_d = abs(pos_mean - neg_mean) / pooled_std
                            mean_diff_results.append({
                                'feature': feature,
                                'pos_mean': pos_mean,
                                'neg_mean': neg_mean,
                                'mean_difference': abs(pos_mean - neg_mean),
                                'cohen_d': cohen_d,
                                'effect_size': 'Large' if cohen_d >= 0.8 else 'Medium' if cohen_d >= 0.5 else 'Small'
                            })
                    except:
                        continue
                        
            mean_diff_results = sorted(mean_diff_results, key=lambda x: x['cohen_d'], reverse=True)
            results['mean_difference'] = mean_diff_results[:top_n]
            
            # 5. Create combined significance ranking
            logger.info(f"   🎯 Creating combined significance ranking...")
            feature_scores = {}
            
            # Normalize and combine scores from different methods
            for method, method_results in results.items():
                if method == 'point_biserial':
                    for i, result in enumerate(method_results):
                        feature = result['feature']
                        score = (top_n - i) / top_n  # Higher rank = higher score
                        feature_scores[feature] = feature_scores.get(feature, 0) + score * 0.25
                        
                elif method == 'f_statistic':
                    for i, result in enumerate(method_results):
                        feature = result['feature']
                        score = (top_n - i) / top_n
                        feature_scores[feature] = feature_scores.get(feature, 0) + score * 0.25
                        
                elif method == 'mutual_information':
                    for i, result in enumerate(method_results):
                        feature = result['feature']
                        score = (top_n - i) / top_n
                        feature_scores[feature] = feature_scores.get(feature, 0) + score * 0.25
                        
                elif method == 'mean_difference':
                    for i, result in enumerate(method_results):
                        feature = result['feature']
                        score = (top_n - i) / top_n
                        feature_scores[feature] = feature_scores.get(feature, 0) + score * 0.25
            
            # Create final combined ranking
            combined_ranking = [{'feature': feature, 'combined_score': score} 
                              for feature, score in feature_scores.items()]
            combined_ranking = sorted(combined_ranking, key=lambda x: x['combined_score'], reverse=True)
            results['combined_ranking'] = combined_ranking[:top_n]
            
            # Log summary results
            logger.info(f"✅ Feature significance analysis completed for {symbol}")
            logger.info(f"   🏆 Top 5 features by combined score:")
            for i, result in enumerate(combined_ranking[:5], 1):
                logger.info(f"      {i}. {result['feature']}: {result['combined_score']:.3f}")
                
            logger.info(f"   📈 Point-biserial top 3:")
            for i, result in enumerate(pb_correlations[:3], 1):
                logger.info(f"      {i}. {result['feature']}: r={result['correlation_raw']:.3f}, p={result['p_value']:.4f}")
                
            logger.info(f"   🔥 F-statistic top 3:")
            for i, result in enumerate(f_results[:3], 1):
                logger.info(f"      {i}. {result['feature']}: F={result['f_score']:.2f}, p={result['p_value']:.4f}")
                
            logger.info(f"   🔄 Mutual information top 3:")
            for i, result in enumerate(mi_results[:3], 1):
                logger.info(f"      {i}. {result['feature']}: MI={result['mi_score']:.4f}")
                
        except Exception as e:
            logger.error(f"❌ Error during feature significance analysis for {symbol}: {e}")
            return {}
            
        return results


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
                
                # Test feature significance analysis on first stock
                if symbol == list(engineered_data.keys())[0]:
                    print(f"\n🔍 Testing feature significance analysis on {symbol}...")
                    significance_results = engineer.analyze_feature_significance(df, symbol, top_n=10)
                    print(f"Analysis completed. Results keys: {list(significance_results.keys())}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        extractor.close()