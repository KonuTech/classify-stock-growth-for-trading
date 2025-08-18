"""
DAG Utilities - Helper functions for Airflow DAGs

This module provides utility functions for determining DAG execution context,
logging configuration, and processing mode detection.

Author: Stock ETL Pipeline
Created: 2025-08-17
"""

import logging
import os
from datetime import datetime, date, timedelta
from typing import Dict, Any, Tuple
from airflow.models import DagRun
from airflow.utils.log.logging_mixin import LoggingMixin

from .polish_trading_calendar import polish_calendar


class ETLLogger(LoggingMixin):
    """Enhanced logger for ETL operations with file and console output."""
    
    def __init__(self, name: str, log_dir: str = "/opt/airflow/logs/etl"):
        """
        Initialize ETL logger with file and console handlers.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
        """
        self.log_dir = log_dir
        self.logger_name = name
        
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file and console handlers."""
        # File handler for detailed logs
        log_file = os.path.join(self.log_dir, f"{self.logger_name}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        """Get the configured logger."""
        return self.logger


def determine_execution_mode(context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Determine if this is a backfill or incremental execution.
    
    Args:
        context: Airflow task context
        
    Returns:
        Tuple of (mode, config) where mode is 'backfill' or 'incremental'
    """
    logger = logging.getLogger(__name__)
    
    # Get execution context with safe access
    dag_run: DagRun = context.get('dag_run')
    execution_date = context.get('ds')  # String format YYYY-MM-DD
    
    # Handle missing ds context (fallback to logical_date or today)
    if not execution_date:
        logical_date = context.get('logical_date')
        if logical_date:
            execution_date = logical_date.strftime('%Y-%m-%d')
        else:
            execution_date = date.today().strftime('%Y-%m-%d')
            logger.warning(f"No execution date in context, using today: {execution_date}")
    
    execution_dt = datetime.strptime(execution_date, '%Y-%m-%d').date()
    today = date.today()
    
    # Get DAG run configuration
    conf = dag_run.conf if dag_run and dag_run.conf else {}
    
    # Mode determination logic
    mode = 'incremental'  # Default
    reason = 'Default mode'
    
    # 1. Check explicit configuration
    if conf.get('mode') == 'backfill':
        mode = 'backfill'
        reason = 'Explicit backfill configuration'
    
    # 2. Check DAG run type
    elif dag_run.run_type in ['backfill', 'manual']:
        mode = 'backfill'
        reason = f'DAG run type: {dag_run.run_type}'
    
    # 3. Check execution date age
    elif execution_dt < (today - timedelta(days=7)):
        mode = 'backfill'
        reason = f'Historical date: {execution_date} (older than 7 days)'
    
    # 4. Check if it's a catchup run
    elif hasattr(dag_run, 'is_backfill') and dag_run.is_backfill:
        mode = 'backfill'
        reason = 'Airflow catchup/backfill run'
    
    # Build configuration
    config = {
        'mode': mode,
        'execution_date': execution_date,
        'execution_date_obj': execution_dt,
        'today': today,
        'dag_run_type': dag_run.run_type if dag_run else 'unknown',
        'is_trading_day': polish_calendar.is_trading_day(execution_dt),
        'reason': reason,
        'manual_conf': conf
    }
    
    # Add mode-specific configuration
    if mode == 'backfill':
        # For backfill, process the exact execution date
        config['target_date'] = execution_dt
        config['date_range'] = conf.get('date_range', 'single_day')
        config['batch_size'] = conf.get('batch_size', 30)
    else:
        # For incremental, process previous trading day
        config['target_date'] = polish_calendar.get_previous_trading_day(today)
        config['date_range'] = 'single_day'
        config['batch_size'] = 1
    
    logger.info(f"Execution mode determined: {mode} ({reason})")
    logger.info(f"Target date for processing: {config['target_date']}")
    logger.info(f"Is trading day: {config['is_trading_day']}")
    
    return mode, config


def should_skip_execution(config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Determine if execution should be skipped based on trading calendar.
    
    Args:
        config: Execution configuration from determine_execution_mode
        
    Returns:
        Tuple of (should_skip, reason)
    """
    target_date = config['target_date']
    mode = config['mode']
    
    # For backfill mode, we might want to process even non-trading days
    # to ensure complete historical coverage
    if mode == 'backfill':
        # Only skip weekends for backfill (holidays might have interesting data)
        if target_date.weekday() >= 5:  # Weekend
            return True, f"Weekend date: {target_date}"
        else:
            return False, f"Backfill mode: processing {target_date}"
    
    # For incremental mode, strictly follow trading calendar
    if not polish_calendar.is_trading_day(target_date):
        holiday_name = polish_calendar.get_holiday_name(target_date)
        if holiday_name:
            return True, f"Polish holiday: {holiday_name} ({target_date})"
        elif target_date.weekday() >= 5:
            return True, f"Weekend: {target_date}"
        else:
            return True, f"Non-trading day: {target_date}"
    
    return False, f"Trading day: proceeding with {target_date}"


def get_schema_from_context(context: Dict[str, Any], default: str = 'prod_stock_data') -> str:
    """
    Get target schema from DAG context or configuration.
    
    Args:
        context: Airflow task context
        default: Default schema if none specified
        
    Returns:
        Target schema name
    """
    dag_run = context.get('dag_run')
    conf = dag_run.conf if dag_run and dag_run.conf else {}
    
    # Check various sources for schema
    schema = (
        conf.get('schema') or 
        context.get('params', {}).get('schema') or
        os.environ.get('ETL_TARGET_SCHEMA') or
        default
    )
    
    return schema


def log_execution_summary(config: Dict[str, Any], results: Dict[str, Any]):
    """
    Log a summary of execution results.
    
    Args:
        config: Execution configuration
        results: Processing results
    """
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("EXECUTION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Mode: {config['mode']}")
    logger.info(f"Target Date: {config['target_date']}")
    logger.info(f"Schema: {results.get('schema', 'unknown')}")
    logger.info(f"Records Processed: {results.get('total_processed', 0)}")
    logger.info(f"Records Inserted: {results.get('total_inserted', 0)}")
    logger.info(f"Records Failed: {results.get('total_failed', 0)}")
    logger.info(f"Success Rate: {results.get('success_rate', 0):.2f}%")
    logger.info(f"Job ID: {results.get('job_id', 'N/A')}")
    logger.info("=" * 60)


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
    """
    Validate a date range for backfill operations.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Validate range
        if start_dt > end_dt:
            return False, "Start date must be before end date"
        
        # Validate against reasonable bounds
        min_date = date(1990, 1, 1)
        max_date = date.today()
        
        if start_dt < min_date:
            return False, f"Start date cannot be before {min_date}"
        
        if end_dt > max_date:
            return False, f"End date cannot be after {max_date}"
        
        # Check for reasonable range size (prevent accidentally huge backfills)
        days_diff = (end_dt - start_dt).days
        if days_diff > 3650:  # 10 years
            return False, f"Date range too large: {days_diff} days (max 3650)"
        
        return True, "Valid date range"
        
    except ValueError as e:
        return False, f"Invalid date format: {e}"