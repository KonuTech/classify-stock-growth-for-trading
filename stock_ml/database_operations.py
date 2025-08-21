"""
ML Database Operations - Support for ML Pipeline DAG
====================================================

Provides database operations for ML pipeline artifacts including:
- Model storage and versioning
- Feature data storage
- Predictions storage
- Backtesting results storage
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
import json
import logging
import numpy as np
import pandas as pd
from sqlalchemy import text
from stock_etl.core.database import get_dev_database, get_test_database, get_prod_database
from .schema_validator import create_validator


class MLDatabaseOperations:
    """Database operations for ML pipeline artifacts"""
    
    def __init__(self, db_host: str = None, target_schema: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Use provided host or detect environment
        if db_host:
            # Set environment variable for DatabaseConfig to use
            import os
            os.environ['DB_HOST'] = db_host
        
        # Set the target schema for operations (dev/test/prod)
        self.target_schema = target_schema or "test_stock_data"
        
        # Validate schema parameter and get appropriate database connection
        schema_to_db_function = {
            "dev_stock_data": get_dev_database,
            "test_stock_data": get_test_database, 
            "prod_stock_data": get_prod_database
        }
        
        if self.target_schema not in schema_to_db_function:
            valid_schemas = list(schema_to_db_function.keys())
            raise ValueError(f"Invalid target_schema '{self.target_schema}'. Must be one of: {valid_schemas}")
        
        # Get the appropriate database connection based on target schema
        self.db = schema_to_db_function[self.target_schema]()
        
        # Initialize schema validator for data validation with correct schema
        self.validator = create_validator(schema=self.target_schema, db_host=db_host)
    
    def save_model_record(
        self, 
        instrument_id: int,
        symbol: str,
        model_version: str,
        model_file_path: str,
        model_hash: str,
        model_size: int,
        hyperparameters: Dict,
        feature_count: int,
        training_results: Dict,
        airflow_context: Dict,
        is_production: bool = False
    ) -> int:
        """
        Save ML model record to ml_models table
        
        Returns:
            model_id: ID of created model record
        """
        # Validate model record data before insertion
        is_valid, errors = self.validator.validate_model_record(
            instrument_id=instrument_id,
            model_version=model_version,
            hyperparameters=hyperparameters,
            training_results=training_results
        )
        
        if not is_valid:
            error_msg = f"Model record validation failed for {symbol}: {'; '.join(errors)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        with self.db.get_session() as session:
            result = session.execute(text('''
                INSERT INTO ml_models (
                    instrument_id, model_version, model_type, model_name,
                    hyperparameters, feature_count, target_variable, target_horizon_days,
                    cv_score, test_accuracy, test_roc_auc, test_f1_score, validation_roc_auc,
                    training_records, validation_records, test_records,
                    training_start_date, training_end_date,
                    model_file_path, model_file_hash, model_size_bytes,
                    feature_names, feature_importance,
                    status, is_production, trained_at,
                    airflow_dag_id, airflow_run_id, training_duration_seconds,
                    created_by
                ) VALUES (
                    :instrument_id, :model_version, :model_type, :model_name,
                    :hyperparameters, :feature_count, :target_variable, :target_horizon_days,
                    :cv_score, :test_accuracy, :test_roc_auc, :test_f1_score, :validation_roc_auc,
                    :training_records, :validation_records, :test_records,
                    :training_start_date, :training_end_date,
                    :model_file_path, :model_file_hash, :model_size_bytes,
                    :feature_names, :feature_importance,
                    :status, :is_production, :trained_at,
                    :airflow_dag_id, :airflow_run_id, :training_duration_seconds,
                    :created_by
                ) RETURNING id
            '''), {
                'instrument_id': instrument_id,
                'model_version': model_version,
                'model_type': 'xgboost_classifier',
                'model_name': f"{symbol}_growth_7d_classifier_{model_version}",
                'hyperparameters': json.dumps(hyperparameters),
                'feature_count': feature_count,
                'target_variable': 'growth_7d',
                'target_horizon_days': 7,
                'cv_score': training_results.get('best_cv_score'),
                'test_accuracy': training_results.get('test_accuracy'),
                'test_roc_auc': training_results.get('test_roc_auc'),
                'test_f1_score': training_results.get('test_f1'),
                'validation_roc_auc': training_results.get('val_roc_auc'),
                'training_records': training_results.get('train_size', 0),
                'validation_records': training_results.get('val_size', 0),
                'test_records': training_results.get('test_size', 0),
                'training_start_date': (datetime.now() - pd.DateOffset(years=2)).date(),
                'training_end_date': datetime.now().date(),
                'model_file_path': model_file_path,
                'model_file_hash': model_hash,
                'model_size_bytes': model_size,
                'feature_names': json.dumps(training_results.get('feature_names', [])),
                'feature_importance': json.dumps(training_results.get('feature_importance', {})),
                'status': 'active',
                'is_production': is_production,
                'trained_at': datetime.now(),
                'airflow_dag_id': airflow_context.get('dag_id'),
                'airflow_run_id': airflow_context.get('run_id'),
                'training_duration_seconds': training_results.get('training_time', 0),
                'created_by': 'airflow'
            })
            
            model_id = result.fetchone()[0]
            session.commit()
            
            self.logger.info(f"✅ Saved model record for {symbol} (model_id: {model_id})")
            return model_id
    
    def save_feature_data(
        self, 
        model_id: int,
        instrument_id: int, 
        feature_df: pd.DataFrame,
        symbol: str
    ) -> int:
        """
        Save feature engineering results to ml_feature_data table
        
        Returns:
            Number of records saved
        """
        # Validate feature data before insertion
        is_valid, errors, cleaned_df = self.validator.validate_feature_data(
            feature_df=feature_df,
            model_id=model_id,
            instrument_id=instrument_id
        )
        
        if not is_valid:
            error_msg = f"Feature data validation failed for {symbol}: {'; '.join(errors)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Use cleaned DataFrame for insertion
        feature_df = cleaned_df
        records_saved = 0
        
        with self.db.get_session() as session:
            for _, row in feature_df.iterrows():
                # Extract key features for individual columns
                additional_features = {}
                
                # Exclude non-numeric metadata columns that shouldn't be stored as features
                excluded_columns = [
                    'trading_date_local', 'open_price', 'high_price', 'low_price',
                    'close_price', 'volume', 'target', 'growth_future_7d',
                    'rsi_14', 'macd_line', 'macd_signal', 'bollinger_upper', 'bollinger_lower',
                    'sma_20', 'sma_50', 'ema_12', 'ema_26', 'stoch_k', 'stoch_d',
                    'williams_r', 'atr_14', 'adx_14', 'cci_20', 'roc_10',
                    # Exclude metadata columns that are not numeric features
                    'symbol', 'currency', 'instrument_type', 'exchange', 'market'
                ]
                
                for col in feature_df.columns:
                    if col not in excluded_columns:
                        try:
                            # Only store numeric values
                            if pd.notnull(row[col]):
                                additional_features[col] = float(row[col])
                            else:
                                additional_features[col] = None
                        except (ValueError, TypeError):
                            # Skip columns that can't be converted to float
                            additional_features[col] = None
                
                session.execute(text('''
                    INSERT INTO ml_feature_data (
                        model_id, instrument_id, trading_date, trading_date_epoch,
                        open_price, high_price, low_price, close_price, volume,
                        rsi_14, macd_line, macd_signal, bollinger_upper, bollinger_lower,
                        sma_20, sma_50, ema_12, ema_26, stoch_k, stoch_d,
                        williams_r, atr_14, adx_14, cci_20, roc_10,
                        additional_features, target, growth_future_7d,
                        feature_completeness, data_quality_score
                    ) VALUES (
                        :model_id, :instrument_id, :trading_date, :trading_date_epoch,
                        :open_price, :high_price, :low_price, :close_price, :volume,
                        :rsi_14, :macd_line, :macd_signal, :bollinger_upper, :bollinger_lower,
                        :sma_20, :sma_50, :ema_12, :ema_26, :stoch_k, :stoch_d,
                        :williams_r, :atr_14, :adx_14, :cci_20, :roc_10,
                        :additional_features, :target, :growth_future_7d,
                        :feature_completeness, :data_quality_score
                    )
                '''), {
                    'model_id': model_id,
                    'instrument_id': instrument_id,
                    'trading_date': row['trading_date_local'].date(),
                    'trading_date_epoch': int(row['trading_date_local'].timestamp()),
                    'open_price': row.get('open_price'),
                    'high_price': row.get('high_price'),
                    'low_price': row.get('low_price'),
                    'close_price': row.get('close_price'),
                    'volume': int(row.get('volume', 0)) if pd.notnull(row.get('volume', 0)) and str(row.get('volume', 0)).replace('.', '').isdigit() else 0,
                    'rsi_14': row.get('rsi_14'),
                    'macd_line': row.get('macd_line'),
                    'macd_signal': row.get('macd_signal'),
                    'bollinger_upper': row.get('bollinger_upper'),
                    'bollinger_lower': row.get('bollinger_lower'),
                    'sma_20': row.get('sma_20'),
                    'sma_50': row.get('sma_50'),
                    'ema_12': row.get('ema_12'),
                    'ema_26': row.get('ema_26'),
                    'stoch_k': row.get('stoch_k'),
                    'stoch_d': row.get('stoch_d'),
                    'williams_r': row.get('williams_r'),
                    'atr_14': row.get('atr_14'),
                    'adx_14': row.get('adx_14'),
                    'cci_20': row.get('cci_20'),
                    'roc_10': row.get('roc_10'),
                    'additional_features': json.dumps(additional_features),
                    'target': bool(row.get('target', False)),
                    'growth_future_7d': row.get('growth_future_7d'),
                    'feature_completeness': 1 - (row.isnull().sum() / len(row)),
                    'data_quality_score': 0.95  # Default quality score
                })
                
                records_saved += 1
            
            session.commit()
            
        self.logger.info(f"✅ Saved {records_saved} feature records for {symbol}")
        return records_saved
    
    def save_predictions(
        self,
        model_id: int,
        instrument_id: int,
        predictions: List[bool],
        probabilities: List[float],
        test_dates: List[date],
        symbol: str,
        airflow_context: Dict
    ) -> int:
        """
        Save model predictions to ml_predictions table
        
        Returns:
            Number of predictions saved
        """
        # Validate predictions data before insertion
        is_valid, errors = self.validator.validate_predictions_data(
            predictions=predictions,
            probabilities=probabilities,
            test_dates=test_dates,
            model_id=model_id,
            instrument_id=instrument_id
        )
        
        if not is_valid:
            error_msg = f"Predictions data validation failed for {symbol}: {'; '.join(errors)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        predictions_saved = 0
        
        with self.db.get_session() as session:
            for i, (pred, prob, pred_date) in enumerate(zip(predictions, probabilities, test_dates)):
                # Handle target date calculation - add 7 days using timedelta
                if isinstance(pred_date, date):
                    target_date = pred_date + timedelta(days=7)
                    # Convert date to datetime for timestamp calculation
                    pred_datetime = datetime.combine(pred_date, datetime.min.time())
                    trading_date_epoch = int(pred_datetime.timestamp())
                else:
                    # pred_date is already datetime
                    target_date = (pred_date + timedelta(days=7)).date()
                    trading_date_epoch = int(pred_date.timestamp())
                
                session.execute(text('''
                    INSERT INTO ml_predictions (
                        model_id, instrument_id, prediction_date, target_date,
                        prediction_horizon_days, trading_date_epoch,
                        predicted_class, prediction_probability, prediction_confidence,
                        trading_signal, signal_strength, holding_period_days,
                        airflow_dag_id, airflow_run_id
                    ) VALUES (
                        :model_id, :instrument_id, :prediction_date, :target_date,
                        :prediction_horizon_days, :trading_date_epoch,
                        :predicted_class, :prediction_probability, :prediction_confidence,
                        :trading_signal, :signal_strength, :holding_period_days,
                        :airflow_dag_id, :airflow_run_id
                    )
                '''), {
                    'model_id': model_id,
                    'instrument_id': instrument_id,
                    'prediction_date': pred_date,
                    'target_date': target_date,
                    'prediction_horizon_days': 7,
                    'trading_date_epoch': trading_date_epoch,
                    'predicted_class': bool(pred),
                    'prediction_probability': float(prob),
                    'prediction_confidence': abs(float(prob) - 0.5) * 2,  # Convert to confidence [0,1]
                    'trading_signal': 'BUY' if prob > 0.6 else ('SELL' if prob < 0.4 else 'HOLD'),
                    'signal_strength': abs(float(prob) - 0.5) * 2,
                    'holding_period_days': 7,
                    'airflow_dag_id': airflow_context.get('dag_id'),
                    'airflow_run_id': airflow_context.get('run_id')
                })
                
                predictions_saved += 1
            
            session.commit()
            
        self.logger.info(f"✅ Saved {predictions_saved} predictions for {symbol}")
        return predictions_saved
    
    def save_backtest_results(
        self,
        model_id: int,
        instrument_id: int,
        backtest_results: Dict,
        symbol: str,
        airflow_context: Dict
    ) -> None:
        """
        Save backtesting results to ml_backtest_results table
        """
        # Validate backtest results before insertion
        is_valid, errors = self.validator.validate_backtest_results(
            backtest_results=backtest_results,
            model_id=model_id,
            instrument_id=instrument_id
        )
        
        if not is_valid:
            error_msg = f"Backtest results validation failed for {symbol}: {'; '.join(errors)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        with self.db.get_session() as session:
            session.execute(text('''
                INSERT INTO ml_backtest_results (
                    model_id, instrument_id, backtest_start_date, backtest_end_date,
                    holding_period_days, probability_threshold, initial_capital, transaction_cost,
                    total_return, annualized_return, sharpe_ratio, max_drawdown, win_rate, profit_factor,
                    total_trades, winning_trades, losing_trades,
                    avg_trade_return, best_trade_return, worst_trade_return,
                    volatility, var_95, calmar_ratio,
                    trade_history, monthly_returns,
                    backtest_quality, quality_score,
                    airflow_dag_id, airflow_run_id
                ) VALUES (
                    :model_id, :instrument_id, :backtest_start_date, :backtest_end_date,
                    :holding_period_days, :probability_threshold, :initial_capital, :transaction_cost,
                    :total_return, :annualized_return, :sharpe_ratio, :max_drawdown, :win_rate, :profit_factor,
                    :total_trades, :winning_trades, :losing_trades,
                    :avg_trade_return, :best_trade_return, :worst_trade_return,
                    :volatility, :var_95, :calmar_ratio,
                    :trade_history, :monthly_returns,
                    :backtest_quality, :quality_score,
                    :airflow_dag_id, :airflow_run_id
                )
            '''), {
                'model_id': model_id,
                'instrument_id': instrument_id,
                'backtest_start_date': (datetime.now() - pd.DateOffset(years=1)).date(),
                'backtest_end_date': datetime.now().date(),
                'holding_period_days': 7,
                'probability_threshold': 0.6,
                'initial_capital': 10000.00,
                'transaction_cost': 0.001,
                'total_return': backtest_results.get('total_return', 0),
                'annualized_return': backtest_results.get('annualized_return', 0),
                'sharpe_ratio': backtest_results.get('sharpe_ratio', 0),
                'max_drawdown': backtest_results.get('max_drawdown', 0),
                'win_rate': backtest_results.get('win_rate', 0),
                'profit_factor': backtest_results.get('profit_factor', 1.0),
                'total_trades': backtest_results.get('total_trades', 0),
                'winning_trades': backtest_results.get('winning_trades', 0),
                'losing_trades': backtest_results.get('losing_trades', 0),
                'avg_trade_return': backtest_results.get('avg_trade_return', 0),
                'best_trade_return': backtest_results.get('best_trade_return', 0),
                'worst_trade_return': backtest_results.get('worst_trade_return', 0),
                'volatility': backtest_results.get('volatility', 0),
                'var_95': backtest_results.get('var_95', 0),
                'calmar_ratio': backtest_results.get('calmar_ratio', 0),
                'trade_history': json.dumps(backtest_results.get('trades', [])),
                'monthly_returns': json.dumps(backtest_results.get('monthly_returns', {})),
                'backtest_quality': self._assess_backtest_quality(backtest_results),
                'quality_score': self._calculate_quality_score(backtest_results),
                'airflow_dag_id': airflow_context.get('dag_id'),
                'airflow_run_id': airflow_context.get('run_id')
            })
            
            session.commit()
            
        self.logger.info(f"✅ Saved backtesting results for {symbol}")
    
    def _assess_backtest_quality(self, results: Dict) -> str:
        """Assess backtest quality based on performance metrics"""
        total_return = results.get('total_return', 0)
        sharpe_ratio = results.get('sharpe_ratio', 0)
        win_rate = results.get('win_rate', 0)
        total_trades = results.get('total_trades', 0)
        
        if total_return > 0.15 and sharpe_ratio > 1.0 and win_rate > 0.55 and total_trades > 10:
            return 'EXCELLENT'
        elif total_return > 0.10 and sharpe_ratio > 0.5 and win_rate > 0.50 and total_trades > 5:
            return 'GOOD'
        elif total_return > 0.05 and total_trades > 3:
            return 'FAIR'
        else:
            return 'POOR'
    
    def _calculate_quality_score(self, results: Dict) -> float:
        """Calculate overall quality score [0,1]"""
        total_return = results.get('total_return', 0)
        sharpe_ratio = results.get('sharpe_ratio', 0)
        win_rate = results.get('win_rate', 0)
        
        # Weighted combination of metrics
        score = (
            min(1.0, max(0.0, total_return * 2)) * 0.4 +  # Total return (capped at 50%)
            min(1.0, max(0.0, sharpe_ratio / 2)) * 0.3 +   # Sharpe ratio (capped at 2.0)
            min(1.0, max(0.0, win_rate)) * 0.3              # Win rate
        )
        
        return round(score, 4)
    
    def get_latest_model(self, instrument_id: int) -> Optional[Dict]:
        """Get latest active model for an instrument"""
        with self.db.get_session() as session:
            result = session.execute(text('''
                SELECT id, model_version, trained_at, test_roc_auc, model_file_path
                FROM ml_models 
                WHERE instrument_id = :instrument_id 
                  AND status = 'active'
                  AND is_production = true
                ORDER BY trained_at DESC
                LIMIT 1
            '''), {'instrument_id': instrument_id})
            
            row = result.fetchone()
            if row:
                return {
                    'model_id': row[0],
                    'model_version': row[1], 
                    'trained_at': row[2],
                    'test_roc_auc': row[3],
                    'model_file_path': row[4]
                }
            return None
    
    def update_prediction_actuals(self, days_back: int = 7) -> int:
        """
        Update prediction accuracy for predictions made N days ago
        
        Args:
            days_back: How many days back to check for actual outcomes
            
        Returns:
            Number of predictions updated
        """
        updated_count = 0
        
        with self.db.get_session() as session:
            # Find predictions that need actual outcome updates
            result = session.execute(text('''
                SELECT p.id, p.instrument_id, p.target_date, p.predicted_class
                FROM ml_predictions p
                WHERE p.target_date = CURRENT_DATE - INTERVAL '%s days'
                  AND p.actual_class IS NULL
            '''), (days_back,))
            
            for row in result.fetchall():
                pred_id, instrument_id, target_date, predicted_class = row
                
                # Get actual price data for the target date and 7 days later
                price_result = session.execute(text('''
                    SELECT 
                        sp1.close_price as start_price,
                        sp2.close_price as end_price
                    FROM stock_prices sp1
                    JOIN stock_prices sp2 ON sp2.stock_id = sp1.stock_id
                        AND sp2.trading_date_local = sp1.trading_date_local + INTERVAL '7 days'
                    WHERE sp1.stock_id = :instrument_id
                      AND sp1.trading_date_local = :target_date
                '''), {
                    'instrument_id': instrument_id,
                    'target_date': target_date
                })
                
                price_row = price_result.fetchone()
                if price_row:
                    start_price, end_price = price_row
                    actual_growth = end_price / start_price
                    actual_return = (end_price - start_price) / start_price
                    actual_class = actual_growth > 1.0
                    prediction_accuracy = predicted_class == actual_class
                    
                    # Update the prediction record
                    session.execute(text('''
                        UPDATE ml_predictions 
                        SET actual_class = :actual_class,
                            actual_return_7d = :actual_return,
                            actual_growth_7d = :actual_growth,
                            prediction_accuracy = :prediction_accuracy,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :pred_id
                    '''), {
                        'actual_class': actual_class,
                        'actual_return': actual_return,
                        'actual_growth': actual_growth,
                        'prediction_accuracy': prediction_accuracy,
                        'pred_id': pred_id
                    })
                    
                    updated_count += 1
            
            session.commit()
            
        self.logger.info(f"✅ Updated {updated_count} prediction actuals")
        return updated_count