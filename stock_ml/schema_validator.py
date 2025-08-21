"""
ML Schema Validator - Data Type Validation Against Database Schema
=================================================================

Validates data types and structure against actual database schema before insertion.
Ensures data completeness and prevents type conversion errors.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, date
from decimal import Decimal
import logging
from sqlalchemy import text
from stock_etl.core.database import get_database_manager


class MLSchemaValidator:
    """Validates ML data against database schema definitions"""
    
    def __init__(self, schema: str = "test_stock_data", db_host: str = None):
        """Initialize schema validator with database connection"""
        self.schema = schema
        self.db = get_database_manager(schema)
        if db_host:
            # Override host for Airflow environment
            self.db.config.host = db_host
        
        self.logger = logging.getLogger(__name__)
        self._schema_cache = {}
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Fetch table schema from database including column types and constraints
        
        Returns:
            Dict with column definitions and constraints
        """
        if table_name in self._schema_cache:
            return self._schema_cache[table_name]
        
        with self.db.get_session() as session:
            # Get column information
            result = session.execute(text(f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    udt_name
                FROM information_schema.columns 
                WHERE table_schema = :schema 
                AND table_name = :table_name
                ORDER BY ordinal_position
            """), {"schema": self.schema, "table_name": table_name})
            
            columns = {}
            for row in result:
                columns[row.column_name] = {
                    'data_type': row.data_type,
                    'udt_name': row.udt_name,
                    'is_nullable': row.is_nullable == 'YES',
                    'column_default': row.column_default,
                    'character_maximum_length': row.character_maximum_length,
                    'numeric_precision': row.numeric_precision,
                    'numeric_scale': row.numeric_scale
                }
            
            # Get check constraints
            constraints_result = session.execute(text(f"""
                SELECT 
                    cc.constraint_name,
                    cc.check_clause
                FROM information_schema.check_constraints cc
                JOIN information_schema.table_constraints tc 
                    ON cc.constraint_name = tc.constraint_name
                WHERE tc.table_schema = :schema 
                AND tc.table_name = :table_name
            """), {"schema": self.schema, "table_name": table_name})
            
            constraints = {}
            for row in constraints_result:
                constraints[row.constraint_name] = row.check_clause
            
            schema_info = {
                'columns': columns,
                'constraints': constraints,
                'table_name': table_name
            }
            
            self._schema_cache[table_name] = schema_info
            return schema_info
    
    def validate_feature_data(self, feature_df: pd.DataFrame, model_id: int, instrument_id: int) -> Tuple[bool, List[str], pd.DataFrame]:
        """
        Validate feature data DataFrame against ml_feature_data table schema
        
        Returns:
            Tuple of (is_valid, error_messages, cleaned_dataframe)
        """
        self.logger.info(f"Validating feature data: {len(feature_df)} records, {len(feature_df.columns)} columns")
        
        schema = self.get_table_schema('ml_feature_data')
        errors = []
        
        # Expected columns from schema
        expected_columns = set(schema['columns'].keys())
        df_columns = set(feature_df.columns)
        
        # Define required columns that must be in the DataFrame
        required_from_df = {
            'trading_date_local', 'open_price', 'high_price', 'low_price', 
            'close_price', 'volume', 'target', 'growth_future_7d'
        }
        
        # Define columns that will be added programmatically
        programmatic_columns = {
            'id', 'model_id', 'instrument_id', 'trading_date', 'trading_date_epoch',
            'feature_completeness', 'data_quality_score', 'created_at'
        }
        
        # Define technical indicator columns that should be present
        technical_indicators = {
            'rsi_14', 'macd_line', 'macd_signal', 'bollinger_upper', 'bollinger_lower',
            'sma_20', 'sma_50', 'ema_12', 'ema_26', 'stoch_k', 'stoch_d',
            'williams_r', 'atr_14', 'adx_14', 'cci_20', 'roc_10'
        }
        
        # Define columns that should NOT be in the DataFrame (metadata)
        excluded_columns = {
            'symbol', 'currency', 'instrument_type', 'exchange', 'market',
            'company_name', 'sector', 'country'
        }
        
        # 1. Clean up excluded metadata columns first
        found_excluded = df_columns.intersection(excluded_columns)
        cleaned_df = feature_df.copy()
        
        for col in found_excluded:
            if col in cleaned_df.columns:
                cleaned_df = cleaned_df.drop(columns=[col])
                self.logger.info(f"Removed excluded column: {col}")
        
        # Update df_columns after cleanup
        df_columns = set(cleaned_df.columns)
        
        # 2. Check for required columns
        missing_required = required_from_df - df_columns
        if missing_required:
            errors.append(f"Missing required columns: {missing_required}")
        
        # 3. Validate data types for each column
        
        # Validate data types for remaining columns
        for col in cleaned_df.columns:
            if col in schema['columns']:
                expected_type = schema['columns'][col]['data_type']
                nullable = schema['columns'][col]['is_nullable']
                
                # Validate specific column types
                try:
                    if col == 'trading_date_local':
                        # Ensure it's a proper date
                        cleaned_df[col] = pd.to_datetime(cleaned_df[col]).dt.date
                    
                    elif col in ['open_price', 'high_price', 'low_price', 'close_price'] + list(technical_indicators):
                        # Numeric price/indicator columns
                        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                        
                        # Check for non-finite values
                        non_finite = cleaned_df[col].isna() | np.isinf(cleaned_df[col])
                        if non_finite.any() and not nullable:
                            errors.append(f"Column {col} has non-finite values but is not nullable")
                    
                    elif col == 'volume':
                        # Volume should be integer
                        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0).astype('int64')
                    
                    elif col in ['target']:
                        # Boolean columns
                        cleaned_df[col] = cleaned_df[col].astype(bool)
                    
                    elif col in ['growth_future_7d']:
                        # Growth percentage
                        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                
                except Exception as e:
                    errors.append(f"Type conversion failed for column {col}: {str(e)}")
        
        # 4. Additional validation: OHLC consistency
        try:
            price_cols = ['open_price', 'high_price', 'low_price', 'close_price']
            if all(col in cleaned_df.columns for col in price_cols):
                # Check OHLC constraints
                invalid_ohlc = (
                    (cleaned_df['high_price'] < cleaned_df['open_price']) |
                    (cleaned_df['high_price'] < cleaned_df['close_price']) |
                    (cleaned_df['high_price'] < cleaned_df['low_price']) |
                    (cleaned_df['open_price'] < cleaned_df['low_price']) |
                    (cleaned_df['close_price'] < cleaned_df['low_price'])
                )
                
                if invalid_ohlc.any():
                    errors.append(f"OHLC consistency violations in {invalid_ohlc.sum()} rows")
        except Exception as e:
            errors.append(f"OHLC validation failed: {str(e)}")
        
        # 5. Prepare additional features JSON
        additional_features_cols = set(cleaned_df.columns) - required_from_df - technical_indicators - programmatic_columns
        if additional_features_cols:
            self.logger.info(f"Additional features to store in JSON: {len(additional_features_cols)} columns")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            self.logger.info("✅ Feature data validation passed")
        else:
            self.logger.error(f"❌ Feature data validation failed: {len(errors)} errors")
            for error in errors:
                self.logger.error(f"  - {error}")
        
        return is_valid, errors, cleaned_df
    
    def validate_predictions_data(self, predictions: List, probabilities: List, test_dates: List, model_id: int, instrument_id: int) -> Tuple[bool, List[str]]:
        """
        Validate predictions data against ml_predictions table schema
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.logger.info(f"Validating predictions data: {len(predictions)} predictions")
        
        schema = self.get_table_schema('ml_predictions')
        errors = []
        
        # Basic length validation
        if not (len(predictions) == len(probabilities) == len(test_dates)):
            errors.append(f"Length mismatch: predictions={len(predictions)}, probabilities={len(probabilities)}, dates={len(test_dates)}")
            return False, errors
        
        # Validate data types
        try:
            # Predictions should be boolean
            if not all(isinstance(p, (bool, int, np.bool_)) for p in predictions):
                errors.append("Predictions must be boolean values")
            
            # Probabilities should be float between 0 and 1
            for i, prob in enumerate(probabilities):
                if not isinstance(prob, (float, int, np.number)):
                    errors.append(f"Probability at index {i} is not numeric")
                elif not 0 <= prob <= 1:
                    errors.append(f"Probability at index {i} is out of range [0,1]: {prob}")
            
            # Dates should be date objects or convertible to dates
            for i, test_date in enumerate(test_dates):
                if not isinstance(test_date, (date, datetime)):
                    # Try to convert if it's a timestamp or string
                    try:
                        if isinstance(test_date, (int, float)):
                            # Assume it's a timestamp
                            converted_date = pd.to_datetime(test_date, unit='s').date()
                        elif isinstance(test_date, str):
                            # Try to parse as date string
                            converted_date = pd.to_datetime(test_date).date()
                        else:
                            errors.append(f"Date at index {i} cannot be converted to date: {type(test_date)}")
                    except Exception:
                        errors.append(f"Date at index {i} conversion failed: {type(test_date)}")
        
        except Exception as e:
            errors.append(f"Data type validation failed: {str(e)}")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            self.logger.info("✅ Predictions data validation passed")
        else:
            self.logger.error(f"❌ Predictions data validation failed: {len(errors)} errors")
        
        return is_valid, errors
    
    def validate_backtest_results(self, backtest_results: Dict, model_id: int, instrument_id: int) -> Tuple[bool, List[str]]:
        """
        Validate backtest results against ml_backtest_results table schema
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.logger.info("Validating backtest results data")
        
        schema = self.get_table_schema('ml_backtest_results')
        errors = []
        
        # Required fields in backtest results
        required_fields = {
            'total_return', 'sharpe_ratio', 'win_rate', 'total_trades'
        }
        
        missing_fields = required_fields - set(backtest_results.keys())
        if missing_fields:
            errors.append(f"Missing required backtest fields: {missing_fields}")
        
        # Validate numeric ranges
        try:
            if 'win_rate' in backtest_results:
                win_rate = backtest_results['win_rate']
                if not 0 <= win_rate <= 1:
                    errors.append(f"Win rate out of range [0,1]: {win_rate}")
            
            if 'total_trades' in backtest_results:
                total_trades = backtest_results['total_trades']
                if not isinstance(total_trades, (int, np.integer)) or total_trades < 0:
                    errors.append(f"Total trades must be non-negative integer: {total_trades}")
            
            # Validate other numeric fields
            numeric_fields = ['total_return', 'sharpe_ratio', 'max_drawdown', 'volatility']
            for field in numeric_fields:
                if field in backtest_results:
                    value = backtest_results[field]
                    if not isinstance(value, (int, float, np.number)):
                        errors.append(f"Field {field} must be numeric: {type(value)}")
        
        except Exception as e:
            errors.append(f"Backtest results validation failed: {str(e)}")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            self.logger.info("✅ Backtest results validation passed")
        else:
            self.logger.error(f"❌ Backtest results validation failed: {len(errors)} errors")
        
        return is_valid, errors
    
    def validate_model_record(self, instrument_id: int, model_version: str, hyperparameters: Dict, training_results: Dict) -> Tuple[bool, List[str]]:
        """
        Validate model record data against ml_models table schema
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.logger.info(f"Validating model record for instrument_id={instrument_id}")
        
        schema = self.get_table_schema('ml_models')
        errors = []
        
        # Validate instrument_id
        if not isinstance(instrument_id, (int, np.integer)) or instrument_id <= 0:
            errors.append(f"Invalid instrument_id: {instrument_id}")
        
        # Validate model_version
        if not isinstance(model_version, str) or len(model_version) == 0:
            errors.append(f"Invalid model_version: {model_version}")
        
        # Validate hyperparameters is a dict
        if not isinstance(hyperparameters, dict):
            errors.append(f"Hyperparameters must be a dictionary: {type(hyperparameters)}")
        
        # Validate training results metrics
        required_metrics = ['test_roc_auc', 'test_accuracy', 'test_f1_score']
        for metric in required_metrics:
            if metric in training_results:
                value = training_results[metric]
                if not isinstance(value, (int, float, np.number)):
                    errors.append(f"Training metric {metric} must be numeric: {type(value)}")
                elif not 0 <= value <= 1:
                    errors.append(f"Training metric {metric} out of range [0,1]: {value}")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            self.logger.info("✅ Model record validation passed")
        else:
            self.logger.error(f"❌ Model record validation failed: {len(errors)} errors")
        
        return is_valid, errors


def create_validator(schema: str = "test_stock_data", db_host: str = None) -> MLSchemaValidator:
    """Factory function to create schema validator"""
    return MLSchemaValidator(schema=schema, db_host=db_host)