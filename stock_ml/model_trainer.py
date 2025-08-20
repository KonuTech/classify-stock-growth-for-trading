"""
XGBoost model training module for stock growth classification.
Implements hyperparameter optimization, model training, and evaluation.
Handles missing values natively and provides superior performance on financial data.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import pickle
import os
from pathlib import Path

import xgboost as xgb
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    precision_recall_curve, roc_curve, accuracy_score, 
    precision_score, recall_score, f1_score
)
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')
# Set up logging using centralized configuration
from .logging_config import get_ml_logger
logger = get_ml_logger(__name__)


class XGBoostTrainer:
    """XGBoost model trainer with hyperparameter optimization and native NaN handling"""
    
    def __init__(self, random_state: int = 42, n_jobs: int = -1):
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.model = None
        self.best_params = None
        self.cv_scores = None
        self.feature_importance = None
        self.training_history = {}
        
    def define_hyperparameter_grid(self, grid_type: str = 'comprehensive') -> Dict:
        """
        Define XGBoost hyperparameter grid for grid search
        
        Args:
            grid_type: Type of grid ('quick', 'comprehensive', 'production')
            
        Returns:
            XGBoost parameter grid dictionary
        """
        if grid_type == 'quick':
            # Fast grid for testing
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [6, 8],
                'learning_rate': [0.1, 0.2],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0],
                'reg_alpha': [0, 0.1],
                'reg_lambda': [1]
            }
        elif grid_type == 'comprehensive':
            # Comprehensive grid for thorough optimization
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [4, 6, 8, 10],
                'learning_rate': [0.05, 0.1, 0.15, 0.2],
                'subsample': [0.7, 0.8, 0.9, 1.0],
                'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
                'reg_alpha': [0, 0.01, 0.1, 0.5],
                'reg_lambda': [1, 1.5, 2]
            }
        elif grid_type == 'production':
            # Production-optimized grid
            param_grid = {
                'n_estimators': [200, 300, 400],
                'max_depth': [6, 8, 10],
                'learning_rate': [0.05, 0.1, 0.15],
                'subsample': [0.8, 0.9],
                'colsample_bytree': [0.8, 0.9],
                'reg_alpha': [0, 0.1],
                'reg_lambda': [1, 1.5]
            }
        else:
            raise ValueError(f"Unknown grid_type: {grid_type}")
            
        logger.info(f"Using {grid_type} XGBoost hyperparameter grid with {np.prod([len(v) for v in param_grid.values()])} combinations")
        return param_grid
        
    def train_with_grid_search(self, X_train: pd.DataFrame, y_train: pd.Series,
                              X_val: pd.DataFrame, y_val: pd.Series,
                              symbol: str = "",
                              grid_type: str = 'comprehensive',
                              cv_folds: int = 5,
                              scoring: str = 'roc_auc') -> Dict[str, Any]:
        """
        Train XGBoost with hyperparameter optimization
        
        Args:
            X_train: Training features (NaN values preserved)
            y_train: Training targets
            X_val: Validation features (NaN values preserved)
            y_val: Validation targets
            symbol: Stock symbol for logging
            grid_type: Hyperparameter grid type
            cv_folds: Number of CV folds
            scoring: Scoring metric for optimization
            
        Returns:
            Training results dictionary
        """
        logger.info(f"{symbol}: Starting XGBoost training with grid search...")
        start_time = datetime.now()
        
        # Calculate class balance for scale_pos_weight
        pos_count = (y_train == 1).sum()
        neg_count = (y_train == 0).sum()
        scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
        
        # Get hyperparameter grid
        param_grid = self.define_hyperparameter_grid(grid_type)
        
        # Initialize base XGBoost model
        xgb_model = xgb.XGBClassifier(
            random_state=self.random_state,
            n_jobs=self.n_jobs,
            scale_pos_weight=scale_pos_weight,
            tree_method='hist',  # Efficient for large datasets
            verbosity=0
        )
        
        # Set up cross-validation
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        
        # Grid search
        grid_search = GridSearchCV(
            estimator=xgb_model,
            param_grid=param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=self.n_jobs,
            verbose=1,
            return_train_score=True
        )
        
        logger.info(f"{symbol}: Fitting grid search with {len(X_train)} training samples...")
        grid_search.fit(X_train, y_train)
        
        # Store best model and parameters
        self.model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        self.cv_scores = grid_search.best_score_
        
        # Validation predictions
        val_predictions = self.model.predict(X_val)
        val_probabilities = self.model.predict_proba(X_val)[:, 1]
        
        # Calculate metrics
        training_time = (datetime.now() - start_time).total_seconds()
        
        results = {
            'model': self.model,
            'best_params': self.best_params,
            'cv_score': self.cv_scores,
            'val_accuracy': accuracy_score(y_val, val_predictions),
            'val_precision': precision_score(y_val, val_predictions),
            'val_recall': recall_score(y_val, val_predictions),
            'val_f1': f1_score(y_val, val_predictions),
            'val_roc_auc': roc_auc_score(y_val, val_probabilities),
            'val_predictions': val_predictions,
            'val_probabilities': val_probabilities,
            'training_time_seconds': training_time,
            'feature_importance': self._calculate_feature_importance(X_train),
            'grid_search_results': grid_search.cv_results_
        }
        
        # Store training history
        self.training_history[symbol] = results
        
        logger.info(f"{symbol}: Training completed in {training_time:.1f} seconds")
        logger.info(f"{symbol}: Best CV score ({scoring}): {self.cv_scores:.4f}")
        logger.info(f"{symbol}: Validation ROC-AUC: {results['val_roc_auc']:.4f}")
        logger.info(f"{symbol}: Best parameters: {self.best_params}")
        
        return results
        
    def _calculate_feature_importance(self, X_train: pd.DataFrame) -> pd.DataFrame:
        """Calculate and sort feature importance"""
        if self.model is None:
            return pd.DataFrame()
            
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        self.feature_importance = feature_importance
        return feature_importance
        
    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series,
                      symbol: str = "") -> Dict[str, Any]:
        """
        Evaluate trained model on test set
        
        Args:
            X_test: Test features
            y_test: Test targets
            symbol: Stock symbol for logging
            
        Returns:
            Evaluation results dictionary
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train_with_grid_search() first.")
            
        logger.info(f"{symbol}: Evaluating model on test set...")
        
        # Predictions
        test_predictions = self.model.predict(X_test)
        test_probabilities = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate comprehensive metrics
        results = {
            'test_accuracy': accuracy_score(y_test, test_predictions),
            'test_precision': precision_score(y_test, test_predictions),
            'test_recall': recall_score(y_test, test_predictions),
            'test_f1': f1_score(y_test, test_predictions),
            'test_roc_auc': roc_auc_score(y_test, test_probabilities),
            'test_predictions': test_predictions,
            'test_probabilities': test_probabilities,
            'confusion_matrix': confusion_matrix(y_test, test_predictions),
            'classification_report': classification_report(y_test, test_predictions, output_dict=True)
        }
        
        # Add to training history
        if symbol in self.training_history:
            self.training_history[symbol]['test_results'] = results
        
        logger.info(f"{symbol}: Test evaluation complete")
        logger.info(f"{symbol}: Test Accuracy: {results['test_accuracy']:.4f}")
        logger.info(f"{symbol}: Test Precision: {results['test_precision']:.4f}")
        logger.info(f"{symbol}: Test Recall: {results['test_recall']:.4f}")
        logger.info(f"{symbol}: Test F1-Score: {results['test_f1']:.4f}")
        logger.info(f"{symbol}: Test ROC-AUC: {results['test_roc_auc']:.4f}")
        
        return results
        
    def generate_model_report(self, symbol: str, save_path: Optional[str] = None) -> str:
        """
        Generate comprehensive model training report
        
        Args:
            symbol: Stock symbol
            save_path: Optional path to save report
            
        Returns:
            Report string
        """
        if symbol not in self.training_history:
            raise ValueError(f"No training history found for {symbol}")
            
        history = self.training_history[symbol]
        
        report_lines = [
            f"XGBOOST MODEL REPORT - {symbol}",
            "=" * 50,
            f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "MODEL CONFIGURATION:",
            f"  Best Parameters: {history['best_params']}",
            f"  Training Time: {history['training_time_seconds']:.1f} seconds",
            "",
            "CROSS-VALIDATION RESULTS:",
            f"  CV Score: {history['cv_score']:.4f}",
            "",
            "VALIDATION SET PERFORMANCE:",
            f"  Accuracy: {history['val_accuracy']:.4f}",
            f"  Precision: {history['val_precision']:.4f}",
            f"  Recall: {history['val_recall']:.4f}",
            f"  F1-Score: {history['val_f1']:.4f}",
            f"  ROC-AUC: {history['val_roc_auc']:.4f}",
            ""
        ]
        
        # Add test results if available
        if 'test_results' in history:
            test_results = history['test_results']
            report_lines.extend([
                "TEST SET PERFORMANCE:",
                f"  Accuracy: {test_results['test_accuracy']:.4f}",
                f"  Precision: {test_results['test_precision']:.4f}",
                f"  Recall: {test_results['test_recall']:.4f}",
                f"  F1-Score: {test_results['test_f1']:.4f}",
                f"  ROC-AUC: {test_results['test_roc_auc']:.4f}",
                "",
                "CONFUSION MATRIX:",
                str(test_results['confusion_matrix']),
                ""
            ])
            
        # Add feature importance
        if 'feature_importance' in history:
            top_features = history['feature_importance'].head(10)
            report_lines.extend([
                "TOP 10 MOST IMPORTANT FEATURES:",
                top_features.to_string(index=False),
                ""
            ])
            
        report = "\n".join(report_lines)
        
        # Save report if path provided
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                f.write(report)
            logger.info(f"{symbol}: Report saved to {save_path}")
            
        return report
        
    def save_model(self, symbol: str, save_path: str):
        """Save trained model to disk"""
        if self.model is None:
            raise ValueError("No model to save. Train a model first.")
            
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'best_params': self.best_params,
            'feature_importance': self.feature_importance,
            'training_history': self.training_history.get(symbol, {}),
            'symbol': symbol,
            'trained_at': datetime.now()
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
            
        logger.info(f"{symbol}: Model saved to {save_path}")
        
    @classmethod
    def load_model(cls, load_path: str) -> 'XGBoostTrainer':
        """Load trained model from disk"""
        with open(load_path, 'rb') as f:
            model_data = pickle.load(f)
            
        trainer = cls()
        trainer.model = model_data['model']
        trainer.best_params = model_data['best_params']
        trainer.feature_importance = model_data['feature_importance']
        trainer.training_history = {model_data['symbol']: model_data['training_history']}
        
        logger.info(f"Model loaded from {load_path}")
        return trainer
        
    def plot_feature_importance(self, symbol: str, top_n: int = 20, 
                               save_path: Optional[str] = None):
        """Plot feature importance"""
        if symbol not in self.training_history:
            raise ValueError(f"No training history found for {symbol}")
            
        feature_importance = self.training_history[symbol]['feature_importance']
        top_features = feature_importance.head(top_n)
        
        plt.figure(figsize=(10, 8))
        sns.barplot(data=top_features, x='importance', y='feature')
        plt.title(f'{symbol} - Top {top_n} Feature Importance')
        plt.xlabel('Importance')
        plt.ylabel('Features')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"{symbol}: Feature importance plot saved to {save_path}")
            
        plt.show()


class MultiStockXGBoostTrainer:
    """Train XGBoost models for multiple stocks"""
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.trainers = {}
        self.results_summary = None
        
    def train_multiple_stocks(self, preprocessed_data: Dict[str, Dict[str, Any]],
                            grid_type: str = 'comprehensive',
                            cv_folds: int = 5) -> Dict[str, Dict[str, Any]]:
        """
        Train XGBoost models for multiple stocks
        
        Args:
            preprocessed_data: Dictionary mapping symbol -> preprocessed data
            grid_type: Hyperparameter grid type
            cv_folds: Number of CV folds
            
        Returns:
            Dictionary of training results
        """
        logger.info(f"Starting training for {len(preprocessed_data)} stocks...")
        
        all_results = {}
        
        for symbol, data in preprocessed_data.items():
            try:
                logger.info(f"Training model for {symbol}...")
                
                # Initialize trainer for this stock
                trainer = XGBoostTrainer(self.random_state)
                
                # Train with grid search
                train_results = trainer.train_with_grid_search(
                    X_train=data['X_train'],
                    y_train=data['y_train'],
                    X_val=data['X_val'],
                    y_val=data['y_val'],
                    symbol=symbol,
                    grid_type=grid_type,
                    cv_folds=cv_folds
                )
                
                # Evaluate on test set
                test_results = trainer.evaluate_model(
                    X_test=data['X_test'],
                    y_test=data['y_test'],
                    symbol=symbol
                )
                
                # Store trainer and results
                self.trainers[symbol] = trainer
                all_results[symbol] = {
                    'training_results': train_results,
                    'test_results': test_results
                }
                
                logger.info(f"Completed training for {symbol}")
                
            except Exception as e:
                logger.error(f"Failed to train model for {symbol}: {e}")
                continue
                
        logger.info(f"Successfully trained models for {len(all_results)} stocks")
        
        # Generate results summary
        self.results_summary = self._generate_results_summary(all_results)
        
        return all_results
        
    def _generate_results_summary(self, all_results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """Generate summary of all training results"""
        summary_data = []
        
        for symbol, results in all_results.items():
            train_res = results['training_results']
            test_res = results['test_results']
            
            summary_data.append({
                'symbol': symbol,
                'cv_score': train_res['cv_score'],
                'val_accuracy': train_res['val_accuracy'],
                'val_roc_auc': train_res['val_roc_auc'],
                'test_accuracy': test_res['test_accuracy'],
                'test_precision': test_res['test_precision'],
                'test_recall': test_res['test_recall'],
                'test_f1': test_res['test_f1'],
                'test_roc_auc': test_res['test_roc_auc'],
                'training_time': train_res['training_time_seconds'],
                'best_n_estimators': train_res['best_params'].get('n_estimators', 'N/A'),
                'best_max_depth': train_res['best_params'].get('max_depth', 'N/A'),
                'best_learning_rate': train_res['best_params'].get('learning_rate', 'N/A')
            })
            
        return pd.DataFrame(summary_data).sort_values('test_roc_auc', ascending=False)
        
    def get_results_summary(self) -> pd.DataFrame:
        """Get training results summary"""
        if self.results_summary is None:
            raise ValueError("No training results available. Run train_multiple_stocks() first.")
        return self.results_summary
        
    def save_all_models(self, save_dir: str):
        """Save all trained models"""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        for symbol, trainer in self.trainers.items():
            model_path = save_path / f"{symbol}_xgb_model.pkl"
            trainer.save_model(symbol, str(model_path))
            
        # Save results summary
        if self.results_summary is not None:
            summary_path = save_path / "training_results_summary.csv"
            self.results_summary.to_csv(summary_path, index=False)
            logger.info(f"Results summary saved to {summary_path}")
            
        logger.info(f"All models saved to {save_dir}")


if __name__ == "__main__":
    # Test with sample data
    import sys
    sys.path.append('.')
    try:
        from .data_extractor import MultiStockDataExtractor
        from .feature_engineering import StockFeatureEngineer
    except ImportError:
        from data_extractor import MultiStockDataExtractor
        from feature_engineering import StockFeatureEngineer
    try:
        from .preprocessing import XGBoostPreprocessor
    except ImportError:
        from preprocessing import XGBoostPreprocessor
    
    # Quick test with XTB data
    extractor = MultiStockDataExtractor()
    try:
        # Get XTB data
        df = extractor.extract_single_stock_data('XTB')
        if df.empty:
            print("No data found for XTB")
            exit()
            
        # Feature engineering
        engineer = StockFeatureEngineer()
        engineered_df = engineer.engineer_all_features(df, 'XTB')
        
        # Split data
        train_df, val_df, test_df = extractor.split_data_chronologically(engineered_df)
        
        # Preprocessing
        preprocessor = XGBoostPreprocessor()
        result = preprocessor.preprocess_single_stock(train_df, val_df, test_df, 'XTB', max_features=20)
        
        # Model training (quick grid for testing)
        trainer = XGBoostTrainer()
        train_results = trainer.train_with_grid_search(
            X_train=result['X_train'],
            y_train=result['y_train'],
            X_val=result['X_val'],
            y_val=result['y_val'],
            symbol='XTB',
            grid_type='quick'
        )
        
        # Test evaluation
        test_results = trainer.evaluate_model(
            X_test=result['X_test'],
            y_test=result['y_test'],
            symbol='XTB'
        )
        
        # Generate report
        report = trainer.generate_model_report('XTB')
        print(report)
        
        print("\n🎉 Model training test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in model training test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        extractor.close()