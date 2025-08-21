"""
High-Performance XGBoost model training module optimized for multi-core systems.
Implements advanced parallelization, GPU acceleration, and memory optimizations.
"""

import pandas as pd
import numpy as np
import logging
import multiprocessing
import psutil
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
# Optional visualization imports (for Airflow DAG compatibility)
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
import warnings

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

def document_model_results(results: Dict[str, Any], symbol: str) -> None:
    """Document model training results"""
    
    try:
        if not results:
            return
            
        # Create documentation directory
        project_root = find_project_root()
        docs_dir = project_root / "docs" / "knowledge_base" / "dataframe_schemas"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create DataFrame from results for documentation
        model_df = pd.DataFrame([{
            'symbol': symbol,
            'cv_score': results.get('best_cv_score', 0),
            'test_accuracy': results.get('test_accuracy', 0), 
            'test_roc_auc': results.get('test_roc_auc', 0),
            'test_f1_score': results.get('test_f1_score', 0),
            'validation_roc_auc': results.get('validation_roc_auc', 0),
            'best_params': str(results.get('best_params', {})),
            'feature_count': len(results.get('feature_names', [])),
            'training_time': results.get('training_time', 0)
        }])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create markdown content
        step_name = results.get('step_name', 'MODEL TRAINING')
        step_desc = results.get('step_description', 'XGBoost model training results with performance metrics and hyperparameters')
        
        md_content = f"""# {step_name} - Model Results DataFrame Schema

**Generated**: {timestamp}  
**Symbol**: {symbol}  
**Pipeline Step**: {step_name}
**Database Table**: ml_model_results  
**Description**: {step_desc}

## Model Performance Summary

- **Cross-Validation Score**: {results.get('best_cv_score', 0):.4f}
- **Test ROC-AUC**: {results.get('test_roc_auc', 0):.4f}
- **Test Accuracy**: {results.get('test_accuracy', 0):.4f}
- **Test F1-Score**: {results.get('test_f1_score', 0):.4f}
- **Feature Count**: {len(results.get('feature_names', []))}
- **Training Time**: {results.get('training_time', 0):.1f} seconds

## Best Hyperparameters

```json
{results.get('best_params', {})}
```

## Column Details

| Column | Data Type | Description |
|--------|-----------|-------------|
| symbol | object | Stock symbol identifier |
| cv_score | float64 | Cross-validation score (best) |
| test_accuracy | float64 | Accuracy on test set |
| test_roc_auc | float64 | ROC-AUC score on test set |
| test_f1_score | float64 | F1-score on test set |
| validation_roc_auc | float64 | ROC-AUC score on validation set |
| best_params | object | Best hyperparameters (JSON string) |
| feature_count | int64 | Number of features used |
| training_time | float64 | Training time in seconds |

## Database Integration Notes

### Recommended PostgreSQL Schema
```sql
CREATE TABLE ml_model_results (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    cv_score DECIMAL(8,6),
    test_accuracy DECIMAL(8,6),
    test_roc_auc DECIMAL(8,6),
    test_f1_score DECIMAL(8,6),
    validation_roc_auc DECIMAL(8,6),
    best_params JSONB,
    feature_count INTEGER,
    training_time DECIMAL(8,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Sample Data

"""
        
        md_content += model_df.to_markdown(index=False, floatfmt=".4f")
        
        # Document feature importance if available
        if 'feature_importance' in results and results['feature_importance']:
            md_content += "\n\n## Feature Importance (Top 10)\n\n"
            importance_items = list(results['feature_importance'].items())[:10]
            md_content += "| Feature | Importance |\n"
            md_content += "|---------|------------|\n"
            for feat, imp in importance_items:
                md_content += f"| {feat} | {imp:.4f} |\n"
        
        # Save model results documentation
        filename = f"step05_model_training_results_{symbol.lower()}.md"
        file_path = docs_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        print(f"📋 Documented model training results: {file_path}")
        
    except Exception as e:
        print(f"❌ Failed to document model results for {symbol}: {e}")

def document_predictions(predictions_data: Dict[str, Any], symbol: str) -> None:
    """Document model predictions DataFrame"""
    
    try:
        if 'test_predictions' not in predictions_data:
            return
            
        # Create predictions DataFrame
        predictions_df = pd.DataFrame({
            'predicted_class': predictions_data['test_predictions'],
            'predicted_probability': predictions_data.get('test_probabilities', [0.5] * len(predictions_data['test_predictions'])),
            'actual_class': predictions_data.get('y_test', []),
            'prediction_correct': predictions_data['test_predictions'] == predictions_data.get('y_test', [])
        })
        
        # Create documentation directory
        project_root = find_project_root()
        docs_dir = project_root / "docs" / "knowledge_base" / "dataframe_schemas"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate prediction statistics
        accuracy = (predictions_df['prediction_correct'].sum() / len(predictions_df)) if len(predictions_df) > 0 else 0
        positive_predictions = predictions_df['predicted_class'].sum()
        positive_rate = positive_predictions / len(predictions_df) if len(predictions_df) > 0 else 0
        
        step_name = predictions_data.get('step_name', 'MODEL PREDICTIONS')
        step_desc = predictions_data.get('step_description', 'Model predictions vs actual outcomes on test set')
        
        md_content = f"""# {step_name} - Predictions DataFrame Schema

**Generated**: {timestamp}  
**Symbol**: {symbol}  
**Pipeline Step**: {step_name}
**Database Table**: ml_predictions  
**Description**: {step_desc}

## Prediction Summary

- **Total Predictions**: {len(predictions_df):,}
- **Prediction Accuracy**: {accuracy:.2%}
- **Positive Predictions**: {positive_predictions} ({positive_rate:.1%})
- **Average Probability**: {predictions_df['predicted_probability'].mean():.4f}

## Column Details

| Column | Data Type | Description |
|--------|-----------|-------------|
| predicted_class | bool | Binary prediction (True/False for growth) |
| predicted_probability | float64 | Prediction probability [0,1] |
| actual_class | bool | Actual outcome (if available) |
| prediction_correct | bool | Whether prediction was correct |

## Sample Data (First 5 Rows)

"""
        
        if len(predictions_df) >= 5:
            md_content += predictions_df.head(5).to_markdown(index=False, floatfmt=".4f")
        
        md_content += """

## Database Integration Notes

### Recommended PostgreSQL Schema
```sql
CREATE TABLE ml_predictions (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_class BOOLEAN NOT NULL,
    predicted_probability DECIMAL(8,6) NOT NULL,
    actual_class BOOLEAN,
    prediction_correct BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_probability CHECK (predicted_probability >= 0 AND predicted_probability <= 1)
);
```

"""
        
        # Save predictions documentation
        filename = f"step06_model_predictions_{symbol.lower()}.md"
        file_path = docs_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        print(f"📋 Documented model predictions: {file_path}")
        
    except Exception as e:
        print(f"❌ Failed to document predictions for {symbol}: {e}")


class HighPerformanceXGBoostTrainer:
    """
    High-performance XGBoost trainer optimized for multi-core CPU systems with GPU acceleration option.
    
    Features:
    - CPU-first design with optional GPU acceleration
    - Automatic hardware detection and optimization
    - Memory-efficient training for large datasets
    - Parallel hyperparameter optimization
    - Advanced tree methods for performance
    
    Args:
        random_state: Random seed for reproducible results
        auto_optimize: Enable automatic hardware optimization
        use_gpu: Enable GPU acceleration if available (default: False)
        force_cpu: Force CPU usage even if GPU is available (default: True for reliability)
    """
    
    def __init__(self, random_state: int = 42, auto_optimize: bool = True, use_gpu: bool = False, force_cpu: bool = True):
        self.random_state = random_state
        self.auto_optimize = auto_optimize
        self.use_gpu = use_gpu and not force_cpu  # Override GPU if force_cpu is True
        self.force_cpu = force_cpu
        
        # Hardware detection
        self.cpu_cores = multiprocessing.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.gpu_available = self._detect_gpu() if use_gpu else False
        
        # Optimized settings based on hardware
        self.n_jobs = self._optimize_n_jobs()
        self.tree_method = self._select_tree_method()
        self.max_bin = self._optimize_max_bin()
        
        # Model state
        self.model = None
        self.best_params = None
        self.cv_scores = None
        self.feature_importance = None
        self.training_history = {}
        
        # Log hardware configuration
        actual_device = self._get_device()
        logger.info(f"🖥️ XGBoost Trainer Configuration:")
        logger.info(f"   CPU Cores: {self.cpu_cores}")
        logger.info(f"   RAM: {self.memory_gb:.1f} GB")
        logger.info(f"   GPU Requested: {'✅ Yes' if use_gpu else '❌ No'}")
        logger.info(f"   GPU Available: {'✅ Yes' if self.gpu_available else '❌ No'}")
        logger.info(f"   Force CPU Mode: {'✅ Yes' if self.force_cpu else '❌ No'}")
        logger.info(f"   Final Device: {'🚀 GPU (CUDA)' if actual_device == 'cuda' else '💻 CPU (Multi-core)'}")
        logger.info(f"   Parallel Jobs: {self.n_jobs if actual_device == 'cpu' else '1 (GPU optimized)'}")
        logger.info(f"   Tree Method: {self.tree_method}")
        logger.info(f"   Max Bins: {self.max_bin}")
        
    def _detect_gpu(self) -> bool:
        """Detect if CUDA-capable GPU is available for XGBoost"""
        try:
            # Check if XGBoost was compiled with CUDA support
            build_info = xgb.build_info()
            if build_info.get('USE_CUDA', False):
                # Test NVIDIA driver availability
                import subprocess
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Test XGBoost GPU functionality
                    try:
                        import numpy as np
                        from sklearn.datasets import make_classification
                        X, y = make_classification(n_samples=100, n_features=10, random_state=42)
                        model = xgb.XGBClassifier(tree_method='hist', device='cuda', n_estimators=1)
                        model.fit(X, y)
                        logger.info("✅ GPU functionality test passed")
                        return True
                    except Exception as gpu_test_error:
                        logger.warning(f"GPU test failed: {gpu_test_error}")
                        return False
        except Exception as e:
            logger.warning(f"GPU detection failed: {e}")
        return False
    
    def _optimize_n_jobs(self) -> int:
        """Use exactly 2 cores per DAG for concurrent execution"""
        # Fixed 2 cores per DAG - simple and predictable
        return 2
    
    def _select_tree_method(self) -> str:
        """Select optimal tree construction method based on hardware"""
        if self.gpu_available:
            return 'hist'      # Use hist with device='cuda' for GPU acceleration
        elif self.memory_gb >= 16:
            return 'hist'      # Fast histogram method for large RAM
        else:
            return 'approx'    # Memory-efficient approximation
            
    def _get_device(self) -> str:
        """Get the optimal device setting for XGBoost"""
        if self.gpu_available and not self.force_cpu:
            return 'cuda'  # Use GPU acceleration
        else:
            return 'cpu'   # Use CPU
    
    def _optimize_max_bin(self) -> int:
        """Optimize max_bin parameter based on available memory"""
        if self.memory_gb >= 32:
            return 512         # High precision for large RAM
        elif self.memory_gb >= 16:
            return 256         # Balanced precision/memory
        else:
            return 128         # Conservative for limited RAM
    
    def define_hyperparameter_grid(self, grid_type: str = 'comprehensive') -> Dict:
        """
        Define optimized XGBoost hyperparameter grid for high-performance systems
        
        Args:
            grid_type: Type of grid ('quick', 'comprehensive', 'production', 'aggressive')
            
        Returns:
            XGBoost parameter grid dictionary optimized for your hardware
        """
        if grid_type == 'quick':
            # Fast grid for testing (optimized for multi-core)
            param_grid = {
                'n_estimators': [200, 400],
                'max_depth': [6, 8, 10],
                'learning_rate': [0.1, 0.15],
                'subsample': [0.8, 0.9],
                'colsample_bytree': [0.8, 0.9],
                'reg_alpha': [0, 0.1],
                'reg_lambda': [1, 1.5]
            }
        elif grid_type == 'comprehensive':
            # Comprehensive grid optimized for your hardware
            param_grid = {
                'n_estimators': [200, 400, 600, 800],
                'max_depth': [4, 6, 8, 10, 12],
                'learning_rate': [0.05, 0.1, 0.15, 0.2],
                'subsample': [0.7, 0.8, 0.9, 1.0],
                'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
                'reg_alpha': [0, 0.01, 0.1, 0.5, 1.0],
                'reg_lambda': [1, 1.5, 2, 3]
            }
        elif grid_type == 'production':
            # Production-optimized grid
            param_grid = {
                'n_estimators': [400, 600, 800, 1000],
                'max_depth': [6, 8, 10, 12],
                'learning_rate': [0.05, 0.1, 0.15],
                'subsample': [0.8, 0.9, 1.0],
                'colsample_bytree': [0.8, 0.9, 1.0],
                'reg_alpha': [0, 0.1, 0.5],
                'reg_lambda': [1, 1.5, 2]
            }
        elif grid_type == 'aggressive':
            # Aggressive grid for powerful systems (your case!)
            param_grid = {
                'n_estimators': [500, 750, 1000, 1500],
                'max_depth': [8, 10, 12, 15],
                'learning_rate': [0.03, 0.05, 0.1, 0.15],
                'subsample': [0.8, 0.85, 0.9, 0.95],
                'colsample_bytree': [0.8, 0.85, 0.9, 0.95],
                'reg_alpha': [0, 0.1, 0.5, 1.0],
                'reg_lambda': [1, 1.5, 2, 3],
                'gamma': [0, 0.1, 0.5, 1.0],  # Additional regularization
                'min_child_weight': [1, 3, 5]  # Additional regularization
            }
        else:
            raise ValueError(f"Unknown grid_type: {grid_type}")
            
        total_combinations = np.prod([len(v) for v in param_grid.values()])
        logger.info(f"Using {grid_type} XGBoost hyperparameter grid with {total_combinations:,} combinations")
        logger.info(f"Estimated training time on {self.cpu_cores} cores: {self._estimate_training_time(total_combinations)} minutes")
        
        return param_grid
    
    def _estimate_training_time(self, combinations: int) -> float:
        """Estimate training time based on hardware and grid size"""
        # Base time per combination (minutes) - varies by hardware
        if self.gpu_available:
            base_time = 0.1  # GPU acceleration
        elif self.cpu_cores >= 16:
            base_time = 0.3  # High-end CPU
        elif self.cpu_cores >= 8:
            base_time = 0.5  # Mid-range CPU
        else:
            base_time = 1.0  # Lower-end CPU
            
        # Parallelization efficiency (not perfect scaling)
        parallel_efficiency = min(0.8, self.cpu_cores / 16)
        
        return (combinations * base_time) / (self.cpu_cores * parallel_efficiency)
    
    def train_with_grid_search(self, X_train: pd.DataFrame, y_train: pd.Series,
                              X_val: pd.DataFrame, y_val: pd.Series,
                              symbol: str = "",
                              grid_type: str = 'comprehensive',
                              cv_folds: int = 5,
                              scoring: str = 'roc_auc',
                              enable_early_stopping: bool = True) -> Dict[str, Any]:
        """
        Train XGBoost with optimized hyperparameter search for high-performance systems
        
        Args:
            X_train: Training features (NaN values preserved)
            y_train: Training targets
            X_val: Validation features (NaN values preserved)
            y_val: Validation targets
            symbol: Stock symbol for logging
            grid_type: Hyperparameter grid type ('quick', 'comprehensive', 'production', 'aggressive')
            cv_folds: Number of CV folds
            scoring: Scoring metric for optimization
            enable_early_stopping: Enable early stopping for faster training
            
        Returns:
            Training results dictionary
        """
        logger.info(f"{symbol}: Starting high-performance XGBoost training...")
        logger.info(f"{symbol}: Using {self.tree_method} method on {self.cpu_cores} cores")
        start_time = datetime.now()
        
        # Calculate class balance for scale_pos_weight
        pos_count = (y_train == 1).sum()
        neg_count = (y_train == 0).sum()
        scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
        
        # Get optimized hyperparameter grid
        param_grid = self.define_hyperparameter_grid(grid_type)
        
        # Initialize optimized XGBoost model with modern API
        xgb_params = {
            'random_state': self.random_state,
            'n_jobs': self.n_jobs if not self.gpu_available else 1,  # Use single job for GPU
            'scale_pos_weight': scale_pos_weight,
            'tree_method': self.tree_method,
            'device': self._get_device(),  # Modern device parameter
            'max_bin': self.max_bin,
            'verbosity': 0,
            # Memory optimizations
            'max_delta_step': 1,  # Conservative for stability
            'grow_policy': 'lossguide',  # Memory efficient for large datasets
        }
        
        # Log training device and configuration
        actual_device = xgb_params['device']
        if actual_device == 'cuda' and self.gpu_available and not self.force_cpu:
            logger.info(f"{symbol}: 🚀 Training with GPU acceleration (CUDA)")
            logger.info(f"{symbol}: Device: {actual_device} | Jobs: 1 (GPU optimized)")
        elif self.force_cpu and self.gpu_available:
            logger.info(f"{symbol}: 💻 Training with CPU (GPU available but forced to CPU)")
            logger.info(f"{symbol}: Device: {actual_device} | Jobs: {self.n_jobs} (CPU multi-core)")
        elif actual_device == 'cpu':
            logger.info(f"{symbol}: 💻 Training with CPU (multi-core)")
            logger.info(f"{symbol}: Device: {actual_device} | Jobs: {self.n_jobs} (CPU parallel)")
        else:
            logger.info(f"{symbol}: ⚙️ Training with device: {actual_device}")
        
        # Add early stopping for faster training
        if enable_early_stopping:
            xgb_params.update({
                'early_stopping_rounds': 50,
                'eval_metric': 'auc'
            })
        
        xgb_model = xgb.XGBClassifier(**xgb_params)
        
        # Set up optimized cross-validation
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        
        # Optimized Grid search with parallel processing
        grid_search = GridSearchCV(
            estimator=xgb_model,
            param_grid=param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=2,  # Reduced to 2 cores per DAG for better concurrency
            verbose=2,  # More detailed progress
            return_train_score=True,
            error_score='raise'  # Better error handling
        )
        
        logger.info(f"{symbol}: Starting grid search with {len(X_train):,} training samples...")
        
        # Prepare validation set for early stopping
        eval_set = [(X_val, y_val)] if enable_early_stopping else None
        
        # Fit with optimizations
        if enable_early_stopping and hasattr(xgb_model, 'fit'):
            # Custom fit with early stopping
            try:
                grid_search.fit(X_train, y_train, 
                              eval_set=eval_set, 
                              verbose=False)
            except:
                # Fallback without early stopping
                logger.warning(f"{symbol}: Early stopping failed, using standard fit")
                grid_search.fit(X_train, y_train)
        else:
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
            'grid_search_results': grid_search.cv_results_,
            'hardware_config': {
                'cpu_cores': self.cpu_cores,
                'memory_gb': self.memory_gb,
                'gpu_available': self.gpu_available,
                'tree_method': self.tree_method
            }
        }
        
        # Store training history
        self.training_history[symbol] = results
        
        logger.info(f"{symbol}: ⚡ High-performance training completed in {training_time:.1f} seconds")
        logger.info(f"{symbol}: 🎯 Best CV score ({scoring}): {self.cv_scores:.4f}")
        logger.info(f"{symbol}: 📊 Validation ROC-AUC: {results['val_roc_auc']:.4f}")
        logger.info(f"{symbol}: ⚙️ Best parameters: {self.best_params}")
        logger.info(f"{symbol}: 💾 Memory usage optimized for {self.memory_gb:.1f}GB RAM")
        
        return results
    
    def _calculate_feature_importance(self, X_train: pd.DataFrame) -> pd.DataFrame:
        """Calculate and sort feature importance using multiple XGBoost methods"""
        if self.model is None:
            return pd.DataFrame()
        
        # Get different importance types
        try:
            booster = self.model.get_booster()
            importance_types = ['weight', 'gain', 'cover']
            
            importance_data = []
            for feature in X_train.columns:
                row = {'feature': feature}
                for imp_type in importance_types:
                    scores = booster.get_score(importance_type=imp_type)
                    row[f'{imp_type}_importance'] = scores.get(f'f{list(X_train.columns).index(feature)}', 0)
                importance_data.append(row)
            
            feature_importance = pd.DataFrame(importance_data)
            
            # Create combined importance score
            feature_importance['combined_importance'] = (
                feature_importance['gain_importance'] * 0.5 +
                feature_importance['cover_importance'] * 0.3 +
                feature_importance['weight_importance'] * 0.2
            )
            
            feature_importance = feature_importance.sort_values('combined_importance', ascending=False)
            
        except:
            # Fallback to standard importance
            feature_importance = pd.DataFrame({
                'feature': X_train.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
        
        self.feature_importance = feature_importance
        return feature_importance
    
    def get_performance_report(self) -> str:
        """Generate hardware performance report"""
        device_info = self._get_device()
        is_using_gpu = (self.gpu_available and not self.force_cpu)
        report = [
            "💻 XGBOOST TRAINING CONFIGURATION REPORT",
            "=" * 50,
            f"Training Mode: {'🚀 GPU (CUDA)' if is_using_gpu else '💻 CPU (Multi-core)'}",
            f"CPU Cores: {self.cpu_cores}",
            f"RAM: {self.memory_gb:.1f} GB",
            f"GPU Requested: {'✅ Yes' if self.use_gpu else '❌ No'}",
            f"GPU Available: {'✅ CUDA Capable' if self.gpu_available else '❌ Not Available'}",
            f"Force CPU Mode: {'✅ Yes' if self.force_cpu else '❌ No'}",
            f"Final XGBoost Device: {device_info.upper()}",
            f"Tree Method: {self.tree_method}",
            f"Parallel Configuration: {self.n_jobs if device_info == 'cpu' else '1 (GPU optimized)'} jobs",
            f"Max Bins: {self.max_bin}",
            "",
            "🚀 CURRENT OPTIMIZATION STATUS:",
            f"{'✅' if self.cpu_cores >= 8 else '⚠️'} Multi-core CPU: {'Excellent' if self.cpu_cores >= 16 else 'Good' if self.cpu_cores >= 8 else 'Limited'} ({self.cpu_cores} cores)",
            f"{'✅' if self.memory_gb >= 16 else '⚠️'} Memory: {'High' if self.memory_gb >= 32 else 'Good' if self.memory_gb >= 16 else 'Standard'} ({self.memory_gb:.1f} GB)",
            f"{'🚀' if is_using_gpu else '💻'} Compute Device: {'GPU CUDA - Ultra Fast!' if is_using_gpu else 'CPU Multi-core - Reliable'}",
            "",
            "💡 CONFIGURATION RECOMMENDATIONS:",
        ]
        
        if self.force_cpu:
            report.append("  💻 Currently using CPU mode (reliable and compatible)")
            if self.gpu_available:
                report.append("  🚀 GPU available: set use_gpu=True, force_cpu=False for 5-10x speedup")
            else:
                report.append("  📱 Install CUDA toolkit for optional GPU acceleration")
        elif is_using_gpu:
            report.append("  🚀 GPU acceleration is active - excellent performance!")
            report.append("  📊 Use 'aggressive' grid type for maximum GPU utilization")
            report.append("  💾 Monitor GPU memory with nvidia-smi during training")
        else:
            report.append("  💻 CPU mode active - good for compatibility and debugging")
            if self.gpu_available:
                report.append("  🚀 Set force_cpu=False to enable available GPU acceleration")
                
        if self.cpu_cores < 16:
            report.append("  🖥️ Consider upgrading to 16+ CPU cores for better parallel processing")
        if self.memory_gb < 32:
            report.append("  🧠 More RAM (32GB+) would allow larger max_bin values for accuracy")
            
        if is_using_gpu:
            report.append("  📈 GPU training is most effective with large datasets (>5K samples)")
        else:
            report.append("  🔧 CPU mode is ideal for development, debugging, and smaller datasets")
        
        return "\n".join(report)


class MultiStockXGBoostTrainer:
    """Train high-performance XGBoost models for multiple stocks"""
    
    def __init__(self, random_state: int = 42, use_gpu: bool = False, force_cpu: bool = True):
        self.random_state = random_state
        self.use_gpu = use_gpu
        self.force_cpu = force_cpu
        self.trainers = {}
        self.results_summary = None
        
    def train_multiple_stocks(self, preprocessed_data: Dict[str, Dict[str, Any]],
                            grid_type: str = 'comprehensive',
                            cv_folds: int = 5) -> Dict[str, Dict[str, Any]]:
        """
        Train high-performance XGBoost models for multiple stocks
        
        Args:
            preprocessed_data: Dictionary mapping symbol -> preprocessed data
            grid_type: Hyperparameter grid type ('quick', 'comprehensive', 'production', 'aggressive')
            cv_folds: Number of CV folds
            
        Returns:
            Dictionary of training results with hardware optimization info
        """
        logger.info(f"Starting high-performance training for {len(preprocessed_data)} stocks...")
        
        all_results = {}
        
        for symbol, data in preprocessed_data.items():
            try:
                logger.info(f"Training high-performance model for {symbol}...")
                
                # Initialize high-performance trainer for this stock
                trainer = HighPerformanceXGBoostTrainer(
                    random_state=self.random_state, 
                    auto_optimize=True,
                    use_gpu=self.use_gpu,
                    force_cpu=self.force_cpu
                )
                
                # Train with optimized grid search
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
                model = train_results['model']
                test_predictions = model.predict(data['X_test'])
                test_probabilities = model.predict_proba(data['X_test'])[:, 1]
                
                from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
                
                test_results = {
                    'test_accuracy': accuracy_score(data['y_test'], test_predictions),
                    'test_precision': precision_score(data['y_test'], test_predictions),
                    'test_recall': recall_score(data['y_test'], test_predictions),
                    'test_f1': f1_score(data['y_test'], test_predictions),
                    'test_roc_auc': roc_auc_score(data['y_test'], test_probabilities),
                    'test_predictions': test_predictions,
                    'test_probabilities': test_probabilities,
                    'confusion_matrix': confusion_matrix(data['y_test'], test_predictions)
                }
                
                # Store trainer and results
                self.trainers[symbol] = trainer
                all_results[symbol] = {
                    'training_results': train_results,
                    'test_results': test_results
                }
                
                # Document model training results
                combined_results = {**train_results, **test_results}
                combined_results['step_name'] = 'STEP 5 - MODEL TRAINING'
                combined_results['step_description'] = 'XGBoost model training results with hyperparameter tuning, cross-validation scores, and test set performance metrics for 7-day growth prediction (improved accuracy over 30-day)'
                document_model_results(combined_results, symbol)
                
                # Document predictions
                predictions_data = {
                    'test_predictions': test_predictions,
                    'test_probabilities': test_probabilities,
                    'y_test': data['y_test'],
                    'step_name': 'STEP 6 - MODEL PREDICTIONS',
                    'step_description': 'Model predictions on test set with probabilities and actual outcomes for accuracy assessment'
                }
                document_predictions(predictions_data, symbol)
                
                logger.info(f"Completed high-performance training for {symbol}")
                
            except Exception as e:
                logger.error(f"Failed to train model for {symbol}: {e}")
                continue
                
        logger.info(f"Successfully trained high-performance models for {len(all_results)} stocks")
        
        # Generate results summary
        self.results_summary = self._generate_results_summary(all_results)
        
        return all_results
        
    def _generate_results_summary(self, all_results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """Generate summary of all training results"""
        summary_data = []
        
        for symbol, results in all_results.items():
            train_res = results['training_results']
            test_res = results['test_results']
            hw_config = train_res.get('hardware_config', {})
            
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
                'gpu_accelerated': hw_config.get('gpu_available', False),
                'cpu_cores': hw_config.get('cpu_cores', 'N/A'),
                'tree_method': hw_config.get('tree_method', 'N/A'),
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
            # Save the trained model
            with open(model_path, 'wb') as f:
                pickle.dump(trainer.model, f)
                
        # Save results summary
        if self.results_summary is not None:
            summary_path = save_path / "training_results_summary.csv"
            self.results_summary.to_csv(summary_path, index=False)
            logger.info(f"High-performance results summary saved to {summary_path}")
            
        logger.info(f"All high-performance models saved to {save_dir}")


# Maintain backward compatibility with existing code
XGBoostTrainer = HighPerformanceXGBoostTrainer