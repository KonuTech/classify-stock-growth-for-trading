"""
Data preprocessing module for XGBoost model training.
Handles missing values, feature selection, and data preparation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from sklearn.feature_selection import SelectFromModel, VarianceThreshold
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb
import warnings

warnings.filterwarnings('ignore')
# Set up logging using centralized configuration
from .logging_config import get_ml_logger
logger = get_ml_logger(__name__)

# Using XGBoost for robust handling of missing values and financial time series
# XGBoost natively handles NaN values and class imbalance via scale_pos_weight


class XGBoostPreprocessor:
    """Preprocessing pipeline for XGBoost training - preserves NaN values"""
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        # No imputer needed - XGBoost handles NaN natively
        self.variance_selector = VarianceThreshold(threshold=0.01)
        self.feature_selector = None
        self.label_encoders = {}
        self.feature_columns = None
        self.selected_features = None
        
    def prepare_features_and_target(self, df: pd.DataFrame, symbol: str) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare feature matrix and target variable
        
        Args:
            df: Engineered DataFrame with features and target
            symbol: Stock symbol for logging
            
        Returns:
            Tuple of (features_df, target_series)
        """
        # Define columns to exclude from features
        exclude_cols = {
            'symbol', 'currency', 'trading_date_local', 'close_price', 'volume',
            'open_price', 'high_price', 'low_price', 'target', 'growth_future_30d',
            # added manually:
            'year', 'year_month', 'year_week', 'year_quarter'
        }
        
        # Get feature columns
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Prepare features
        X = df[feature_cols].copy()
        
        # Prepare target
        if 'target' not in df.columns:
            raise ValueError(f"{symbol}: No target variable found in DataFrame")
            
        y = df['target'].copy()
        
        logger.info(f"{symbol}: Prepared {len(feature_cols)} features, {len(y)} samples")
        logger.info(f"{symbol}: Target distribution - Positive: {(y == 1).mean():.2%}, Negative: {(y == 0).mean():.2%}")
        
        # Store feature column names
        self.feature_columns = feature_cols
        
        return X, y
        
    def handle_missing_values(self, X_train: pd.DataFrame, X_val: pd.DataFrame, 
                            X_test: pd.DataFrame, symbol: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Preserve missing values for XGBoost native handling
        
        Args:
            X_train: Training features
            X_val: Validation features  
            X_test: Test features
            symbol: Stock symbol for logging
            
        Returns:
            Tuple of DataFrames with NaN values preserved
        """
        logger.info(f"{symbol}: Preserving missing values for XGBoost native handling...")
        
        # Check missing values for logging
        train_missing = X_train.isnull().sum().sum()
        val_missing = X_val.isnull().sum().sum()
        test_missing = X_test.isnull().sum().sum()
        
        logger.info(f"{symbol}: Missing values - Train: {train_missing}, Val: {val_missing}, Test: {test_missing}")
        
        # Only remove completely empty columns (100% NaN)
        completely_missing_cols = X_train.columns[X_train.isnull().all()].tolist()
        if completely_missing_cols:
            logger.warning(f"{symbol}: Dropping {len(completely_missing_cols)} completely missing columns: {completely_missing_cols[:5]}...")
            X_train = X_train.drop(columns=completely_missing_cols)
            X_val = X_val.drop(columns=completely_missing_cols)
            X_test = X_test.drop(columns=completely_missing_cols)
        
        logger.info(f"{symbol}: XGBoost will handle {train_missing - len(completely_missing_cols) * len(X_train)} NaN values natively")
        logger.info(f"{symbol}: Final feature count: {X_train.shape[1]}")
        
        return X_train, X_val, X_test
        
    def remove_low_variance_features(self, X_train: pd.DataFrame, X_val: pd.DataFrame,
                                   X_test: pd.DataFrame, symbol: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Remove features with low variance
        
        Args:
            X_train: Training features
            X_val: Validation features
            X_test: Test features  
            symbol: Stock symbol for logging
            
        Returns:
            Tuple of filtered DataFrames
        """
        logger.info(f"{symbol}: Removing low variance features...")
        
        original_features = X_train.shape[1]
        
        # Fit variance selector on training data
        X_train_filtered = self.variance_selector.fit_transform(X_train)
        X_val_filtered = self.variance_selector.transform(X_val)
        X_test_filtered = self.variance_selector.transform(X_test)
        
        # Get selected feature names
        selected_mask = self.variance_selector.get_support()
        selected_feature_names = [name for name, selected in zip(X_train.columns, selected_mask) if selected]
        
        # Convert back to DataFrames
        X_train_df = pd.DataFrame(X_train_filtered, columns=selected_feature_names, index=X_train.index)
        X_val_df = pd.DataFrame(X_val_filtered, columns=selected_feature_names, index=X_val.index)
        X_test_df = pd.DataFrame(X_test_filtered, columns=selected_feature_names, index=X_test.index)
        
        logger.info(f"{symbol}: Variance filtering: {original_features} -> {len(selected_feature_names)} features")
        
        return X_train_df, X_val_df, X_test_df
        
    def select_features_by_importance(self, X_train: pd.DataFrame, y_train: pd.Series,
                                    X_val: pd.DataFrame, X_test: pd.DataFrame,
                                    max_features: int = 50, symbol: str = "") -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Select features using XGBoost feature importance
        
        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            X_test: Test features
            max_features: Maximum number of features to select
            symbol: Stock symbol for logging
            
        Returns:
            Tuple of feature-selected DataFrames
        """
        logger.info(f"{symbol}: Selecting top {max_features} features by XGBoost importance...")
        
        # Calculate class weights for imbalanced data
        pos_count = (y_train == 1).sum()
        neg_count = (y_train == 0).sum()
        scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
        
        # Use XGBoost for feature selection (handles NaN natively)
        xgb_selector = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=self.random_state,
            scale_pos_weight=scale_pos_weight,
            n_jobs=-1,
            verbosity=0
        )
        
        # Fit selector - XGBoost handles NaN values automatically
        self.feature_selector = SelectFromModel(
            xgb_selector,
            max_features=max_features,
            threshold=-np.inf  # Select top max_features regardless of threshold
        )
        
        # Transform datasets
        X_train_selected = self.feature_selector.fit_transform(X_train, y_train)
        X_val_selected = self.feature_selector.transform(X_val)
        X_test_selected = self.feature_selector.transform(X_test)
        
        # Get selected feature names
        selected_mask = self.feature_selector.get_support()
        self.selected_features = [name for name, selected in zip(X_train.columns, selected_mask) if selected]
        
        # Convert to DataFrames
        X_train_df = pd.DataFrame(X_train_selected, columns=self.selected_features, index=X_train.index)
        X_val_df = pd.DataFrame(X_val_selected, columns=self.selected_features, index=X_val.index)
        X_test_df = pd.DataFrame(X_test_selected, columns=self.selected_features, index=X_test.index)
        
        logger.info(f"{symbol}: Selected {len(self.selected_features)} features using XGBoost")
        logger.info(f"{symbol}: Class balance - Scale pos weight: {scale_pos_weight:.2f}")
        logger.debug(f"{symbol}: Selected features: {self.selected_features}")
        
        return X_train_df, X_val_df, X_test_df
        
    def analyze_class_distribution(self, y_train: pd.Series, symbol: str = "") -> Dict[str, Any]:
        """
        Analyze class distribution without synthetic balancing
        
        Args:
            y_train: Training target
            symbol: Stock symbol for logging
            
        Returns:
            Class distribution analysis
        """
        distribution = y_train.value_counts(normalize=True)
        distribution_counts = y_train.value_counts()
        
        analysis = {
            'positive_ratio': distribution.get(1, 0),
            'negative_ratio': distribution.get(0, 0),
            'positive_count': distribution_counts.get(1, 0),
            'negative_count': distribution_counts.get(0, 0),
            'total_samples': len(y_train),
            'imbalance_ratio': distribution_counts.get(0, 1) / distribution_counts.get(1, 1)
        }
        
        logger.info(f"{symbol}: Class distribution - Positive: {analysis['positive_ratio']:.2%} ({analysis['positive_count']} samples)")
        logger.info(f"{symbol}: Class distribution - Negative: {analysis['negative_ratio']:.2%} ({analysis['negative_count']} samples)")
        logger.info(f"{symbol}: Imbalance ratio: {analysis['imbalance_ratio']:.2f}:1")
        
        # Provide recommendations
        if analysis['imbalance_ratio'] > 3:
            logger.warning(f"{symbol}: High class imbalance detected. Recommend using scale_pos_weight={analysis['imbalance_ratio']:.2f} in XGBoost.")
        elif analysis['imbalance_ratio'] > 2:
            logger.info(f"{symbol}: Moderate class imbalance. scale_pos_weight={analysis['imbalance_ratio']:.2f} recommended.")
        else:
            logger.info(f"{symbol}: Classes relatively balanced.")
            
        return analysis
            
    def preprocess_single_stock(self, train_df: pd.DataFrame, val_df: pd.DataFrame, 
                              test_df: pd.DataFrame, symbol: str,
                              max_features: int = 50) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline for a single stock
        
        Args:
            train_df: Training DataFrame with features and target
            val_df: Validation DataFrame
            test_df: Test DataFrame  
            symbol: Stock symbol
            max_features: Maximum number of features to select
            
        Returns:
            Dictionary with preprocessed data and metadata
        """
        logger.info(f"Starting preprocessing for {symbol}...")
        
        # Prepare features and targets
        X_train, y_train = self.prepare_features_and_target(train_df, symbol)
        X_val, y_val = self.prepare_features_and_target(val_df, symbol)
        X_test, y_test = self.prepare_features_and_target(test_df, symbol)
        
        # Handle missing values
        X_train, X_val, X_test = self.handle_missing_values(X_train, X_val, X_test, symbol)
        
        # Remove low variance features
        X_train, X_val, X_test = self.remove_low_variance_features(X_train, X_val, X_test, symbol)
        
        # Feature selection by importance
        X_train, X_val, X_test = self.select_features_by_importance(
            X_train, y_train, X_val, X_test, max_features, symbol
        )
        
        # Analyze class distribution (no synthetic balancing)
        class_analysis = self.analyze_class_distribution(y_train, symbol)
        
        result = {
            'X_train': X_train,
            'y_train': y_train,
            'X_val': X_val,
            'y_val': y_val,
            'X_test': X_test,
            'y_test': y_test,
            'selected_features': self.selected_features,
            'original_feature_count': len(self.feature_columns),
            'final_feature_count': len(self.selected_features),
            'training_samples': len(y_train),
            'validation_samples': len(y_val),
            'test_samples': len(y_test),
            'class_analysis': class_analysis
        }
        
        logger.info(f"{symbol}: Preprocessing complete")
        logger.info(f"{symbol}: Features: {result['original_feature_count']} -> {result['final_feature_count']}")
        logger.info(f"{symbol}: Training samples: {len(y_train)} (XGBoost handles imbalance natively)")
        
        return result
        
    def preprocess_multiple_stocks(self, split_data: Dict[str, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]],
                                 max_features: int = 50) -> Dict[str, Dict[str, Any]]:
        """
        Preprocess data for multiple stocks
        
        Args:
            split_data: Dictionary mapping symbol -> (train_df, val_df, test_df)
            max_features: Maximum features to select per stock
            
        Returns:
            Dictionary mapping symbol -> preprocessed_data
        """
        preprocessed_data = {}
        
        for symbol, (train_df, val_df, test_df) in split_data.items():
            try:
                # Create new preprocessor for each stock to avoid cross-contamination
                stock_preprocessor = XGBoostPreprocessor(self.random_state)
                
                result = stock_preprocessor.preprocess_single_stock(
                    train_df, val_df, test_df, symbol, max_features
                )
                
                # Also store the preprocessor for this stock
                result['preprocessor'] = stock_preprocessor
                
                preprocessed_data[symbol] = result
                
            except Exception as e:
                logger.error(f"Failed to preprocess {symbol}: {e}")
                continue
                
        logger.info(f"Successfully preprocessed {len(preprocessed_data)} stocks")
        return preprocessed_data
        
    def get_preprocessing_summary(self, preprocessed_data: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """Generate summary of preprocessing results"""
        summary_data = []
        
        for symbol, data in preprocessed_data.items():
            class_analysis = data.get('class_analysis', {})
            summary_data.append({
                'symbol': symbol,
                'original_features': data['original_feature_count'],
                'selected_features': data['final_feature_count'],
                'train_samples': data['training_samples'],
                'val_samples': data['validation_samples'],
                'test_samples': data['test_samples'],
                'positive_ratio': f"{class_analysis.get('positive_ratio', 0):.2%}",
                'imbalance_ratio': f"{class_analysis.get('imbalance_ratio', 0):.1f}:1"
            })
            
        summary_df = pd.DataFrame(summary_data)
        return summary_df


if __name__ == "__main__":
    # Test preprocessing with sample data
    import sys
    sys.path.append('.')
    try:
        from .data_extractor import MultiStockDataExtractor
        from .feature_engineering import StockFeatureEngineer
    except ImportError:
        from data_extractor import MultiStockDataExtractor
        from feature_engineering import StockFeatureEngineer
    
    # Test pipeline
    extractor = MultiStockDataExtractor()
    try:
        # Extract and engineer features
        all_data = extractor.extract_all_stocks_data()
        quality_data = extractor.filter_stocks_by_data_quality(all_data, min_records=300)
        
        engineer = StockFeatureEngineer()
        engineered_data = engineer.engineer_multiple_stocks(quality_data)
        
        # Split data
        split_data = extractor.split_all_stocks_data(engineered_data)
        
        # Preprocessing
        preprocessor = XGBoostPreprocessor()
        preprocessed_data = preprocessor.preprocess_multiple_stocks(split_data, max_features=30)
        
        # Summary
        summary = preprocessor.get_preprocessing_summary(preprocessed_data)
        print(summary)
        
        # Example: Show XTB preprocessing results
        if 'XTB' in preprocessed_data:
            xtb_data = preprocessed_data['XTB']
            print(f"\nXTB preprocessing results:")
            print(f"Selected features: {xtb_data['selected_features'][:10]}...")  # Show first 10
            print(f"Training set shape: {xtb_data['X_train'].shape}")
            print(f"Target balance: {xtb_data['y_train'].value_counts(normalize=True)}")
        
    except Exception as e:
        logger.error(f"Error in preprocessing test: {e}")
    finally:
        extractor.close()