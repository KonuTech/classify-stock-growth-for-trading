"""
Stock Growth Classification ML Pipeline

A comprehensive machine learning pipeline for predicting stock growth using XGBoost classification.
Includes data extraction, feature engineering, model training, and backtesting capabilities.
"""

from .data_extractor import MultiStockDataExtractor
from .feature_engineering import StockFeatureEngineer
from .preprocessing import XGBoostPreprocessor
from .model_trainer import XGBoostTrainer, MultiStockXGBoostTrainer
from .backtesting import TradingBacktester
from .complete_pipeline import StockGrowthClassificationPipeline

__version__ = "1.0.0"
__author__ = "Stock ML Pipeline"

__all__ = [
    'MultiStockDataExtractor',
    'StockFeatureEngineer', 
    'XGBoostPreprocessor',
    'XGBoostTrainer',
    'MultiStockXGBoostTrainer',
    'TradingBacktester',
    'StockGrowthClassificationPipeline'
]