"""
Stock ETL Pipeline - Unified Airflow DAG

This DAG provides a comprehensive data pipeline for loading stock prices, indices,
and market data with full business and metadata tracking:

Business Data:
- Stock prices (OHLCV, volume, adjustments, splits, dividends)
- Index prices (OHLV, market cap, constituent data)
- Instrument metadata and company financials
- Data source tracking and statistics

ETL Metadata:
- Complete job lifecycle tracking with Airflow context
- Per-instrument processing details and timing
- Data quality validation results and metrics
- Error handling and retry logic

Author: Stock ETL Pipeline
Created: 2025-08-17
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import time
import json

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Import utilities from the utils package
import sys
import os
sys.path.append('/opt/airflow/stock_etl')

from utils.dag_utils import (
    determine_execution_mode, 
    should_skip_execution, 
    get_schema_from_context,
    log_execution_summary,
    ETLLogger
)
from utils.polish_trading_calendar import polish_calendar

# Import ETL core modules (commented out for testing)
# from core.etl_orchestrator import ETLOrchestrator
# from core.config import ETLConfig


# DAG Configuration
default_args = {
    'owner': 'stock-etl',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': True,  # Enable catchup for backfill support
}

# DAG definition
dag = DAG(
    'stock_etl_unified_pipeline',
    default_args=default_args,
    description='Unified stock data ETL pipeline with comprehensive metadata tracking',
    schedule='0 18 * * 1-5',  # Run at 6 PM on weekdays
    max_active_runs=1,  # Prevent concurrent runs
    tags=['stock-data', 'etl', 'production'],
    params={
        'schema': 'prod_stock_data',
        'mode': 'incremental', 
        'instruments': 'all',
        'data_sources': 'stooq',
        'enable_validation': True,
        'batch_size': 50
    }
)


def check_execution_prerequisites(**context) -> str:
    """
    Check if execution should proceed based on trading calendar and configuration.
    
    Returns:
        Task ID to branch to: 'skip_execution' or 'proceed_with_etl'
    """
    logger = ETLLogger('prerequisite_check').get_logger()
    
    try:
        # Determine execution mode and configuration
        mode, config = determine_execution_mode(context)
        
        # Check if execution should be skipped
        should_skip, skip_reason = should_skip_execution(config)
        
        if should_skip:
            logger.info(f"Skipping execution: {skip_reason}")
            context['task_instance'].xcom_push(key='skip_reason', value=skip_reason)
            return 'skip_execution'
        
        # Store execution config in XCom for downstream tasks
        context['task_instance'].xcom_push(key='execution_config', value=config)
        logger.info(f"Prerequisites passed - proceeding with {mode} mode")
        return 'proceed_with_etl'
        
    except Exception as e:
        logger.error(f"Error in prerequisite check: {e}")
        raise


def create_etl_job_record(**context) -> int:
    """
    Create ETL job record with comprehensive Airflow metadata.
    
    Returns:
        ETL job ID
    """
    logger = ETLLogger('job_creation').get_logger()
    
    try:
        # Get execution configuration
        execution_config = context['task_instance'].xcom_pull(
            task_ids='check_prerequisites', 
            key='execution_config'
        )
        
        target_schema = get_schema_from_context(context)
        
        # Create job metadata
        job_metadata = {
            'airflow_context': {
                'dag_id': context['dag'].dag_id,
                'task_id': context['task'].task_id,
                'run_id': context['run_id'],
                'execution_date': context['ds'],
                'logical_date': context['logical_date'].isoformat() if context.get('logical_date') else None,
                'dag_run_conf': context.get('dag_run').conf if context.get('dag_run') else {}
            },
            'execution_config': {
                'mode': execution_config['mode'],
                'target_date': execution_config['target_date'].isoformat(),
                'target_schema': target_schema,
                'is_trading_day': execution_config['is_trading_day'],
                'reason': execution_config['reason']
            },
            'runtime_params': dict(context['params']),
            'system_info': {
                'airflow_version': context.get('var', {}).get('value', {}).get('AIRFLOW_VERSION', 'unknown'),
                'python_version': sys.version.split()[0],
                'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown'
            }
        }
        
        # Determine job type
        if execution_config['mode'] == 'backfill':
            job_type = 'historical_backfill'
        else:
            job_type = 'daily_incremental'
        
        # Insert ETL job record
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                insert_sql = f"""
                INSERT INTO {target_schema}.etl_jobs (
                    job_name, job_type, target_instrument_type, status, 
                    started_at, started_at_epoch,
                    target_date_range_start, target_date_range_end,
                    airflow_dag_id, airflow_task_id, airflow_run_id,
                    metadata
                ) VALUES (
                    %s, %s, %s, %s, 
                    %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s
                ) RETURNING id
                """
                
                started_at = datetime.now()
                cursor.execute(insert_sql, (
                    f"{context['dag'].dag_id}_{execution_config['target_date'].strftime('%Y%m%d')}",
                    job_type,
                    'stock',  # Will process multiple types
                    'running',
                    started_at,
                    int(started_at.timestamp()),
                    execution_config['target_date'],
                    execution_config['target_date'],
                    context['dag'].dag_id,
                    context['task'].task_id,
                    context['run_id'],
                    json.dumps(job_metadata)
                ))
                
                job_id = cursor.fetchone()[0]
                conn.commit()
        
        logger.info(f"Created ETL job record: {job_id}")
        return job_id
        
    except Exception as e:
        logger.error(f"Failed to create ETL job record: {e}")
        raise


def extract_and_transform_data(**context) -> Dict[str, Any]:
    """
    Extract data from sources and apply transformations with detailed tracking.
    
    Returns:
        Processing results summary
    """
    logger = ETLLogger('extract_transform').get_logger()
    start_time = time.time()
    
    try:
        # Get job context
        job_id = context['task_instance'].xcom_pull(task_ids='create_etl_job')
        execution_config = context['task_instance'].xcom_pull(
            task_ids='check_prerequisites', 
            key='execution_config'
        )
        target_schema = get_schema_from_context(context)
        
        # Mock extraction data (would be replaced with real ETL orchestrator)
        target_date = execution_config['target_date']
        instruments = context['params'].get('instruments', 'all')
        
        logger.info(f"Extracting data for {target_date} - instruments: {instruments}")
        
        # Simulate data extraction with realistic structure
        extracted_data = {
            'stocks': [
                {
                    'symbol': 'XTB',
                    'trading_date': target_date,
                    'open_price': 6.75,
                    'high_price': 6.85,
                    'low_price': 6.65,
                    'close_price': 6.80,
                    'volume': 750000,
                    'adjusted_close': 6.80,
                    'split_factor': 1.0,
                    'dividend_amount': 0.0,
                    'data_source': 'stooq',
                    'raw_data_hash': 'abc123def456'
                },
                {
                    'symbol': 'PKN',
                    'trading_date': target_date,
                    'open_price': 87.50,
                    'high_price': 89.20,
                    'low_price': 86.80,
                    'close_price': 88.75,
                    'volume': 1200000,
                    'adjusted_close': 88.75,
                    'split_factor': 1.0,
                    'dividend_amount': 0.0,
                    'data_source': 'stooq',
                    'raw_data_hash': 'def456ghi789'
                }
            ],
            'indices': [
                {
                    'symbol': 'WIG',
                    'trading_date': target_date,
                    'open_value': 75500.0,
                    'high_value': 76200.0,
                    'low_value': 75200.0,
                    'close_value': 75900.0,
                    'trading_volume': 25000,
                    'total_market_cap': 750000000000.0,
                    'constituents_traded': 350,
                    'data_source': 'stooq',
                    'raw_data_hash': 'ghi789jkl012'
                }
            ]
        }
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Update data source statistics
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                UPDATE {target_schema}.data_sources 
                SET total_fetches = total_fetches + 1,
                    last_successful_fetch = %s,
                    last_successful_fetch_epoch = %s
                WHERE name = 'stooq'
                """, (datetime.now(), int(time.time())))
                conn.commit()
        
        results = {
            'data': extracted_data,
            'total_records': len(extracted_data['stocks']) + len(extracted_data['indices']),
            'processing_time_ms': processing_time_ms,
            'data_sources': ['stooq'],
            'target_date': target_date.isoformat(),
            'status': 'success'
        }
        
        logger.info(f"Extraction completed: {results['total_records']} records in {processing_time_ms}ms")
        return results
        
    except Exception as e:
        logger.error(f"Extract/transform failed: {e}")
        # Update job status to failed
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        job_id = context['task_instance'].xcom_pull(task_ids='create_etl_job')
        if job_id:
            with postgres_hook.get_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                    UPDATE {get_schema_from_context(context)}.etl_jobs 
                    SET status = 'failed', error_message = %s 
                    WHERE id = %s
                    """, (str(e), job_id))
                    conn.commit()
        raise


def load_data_to_database(**context) -> Dict[str, Any]:
    """
    Load transformed data with comprehensive metadata tracking.
    
    Returns:
        Load operation results
    """
    logger = ETLLogger('data_load').get_logger()
    start_time = time.time()
    
    try:
        # Get context data
        job_id = context['task_instance'].xcom_pull(task_ids='create_etl_job')
        extract_results = context['task_instance'].xcom_pull(task_ids='extract_and_transform')
        target_schema = get_schema_from_context(context)
        
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        records_inserted = 0
        records_updated = 0
        records_failed = 0
        
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                # Process stock data
                for stock_data in extract_results['data']['stocks']:
                    try:
                        instrument_start_time = time.time()
                        
                        # Get or create base instrument
                        cursor.execute(f"""
                        SELECT id FROM {target_schema}.base_instruments 
                        WHERE symbol = %s AND instrument_type = 'stock'
                        """, (stock_data['symbol'],))
                        
                        result = cursor.fetchone()
                        if not result:
                            # Create missing instrument (would normally be handled by reference data job)
                            logger.warning(f"Instrument {stock_data['symbol']} not found - skipping")
                            continue
                        
                        instrument_id = result[0]
                        
                        # Get stock ID
                        cursor.execute(f"""
                        SELECT id FROM {target_schema}.stocks 
                        WHERE instrument_id = %s
                        """, (instrument_id,))
                        
                        stock_result = cursor.fetchone()
                        if not stock_result:
                            logger.warning(f"Stock record for {stock_data['symbol']} not found - skipping")
                            continue
                        
                        stock_id = stock_result[0]
                        
                        # Insert stock price data
                        cursor.execute(f"""
                        INSERT INTO {target_schema}.stock_prices (
                            stock_id, trading_date_local, trading_date_utc, trading_date_epoch,
                            trading_datetime_utc, trading_datetime_epoch,
                            open_price, high_price, low_price, close_price, volume,
                            adjusted_close, split_factor, dividend_amount,
                            data_source, raw_data_hash
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) ON CONFLICT (stock_id, trading_date_local) 
                        DO UPDATE SET 
                            open_price = EXCLUDED.open_price,
                            high_price = EXCLUDED.high_price,
                            low_price = EXCLUDED.low_price,
                            close_price = EXCLUDED.close_price,
                            volume = EXCLUDED.volume,
                            adjusted_close = EXCLUDED.adjusted_close,
                            raw_data_hash = EXCLUDED.raw_data_hash
                        """, (
                            stock_id, stock_data['trading_date'], stock_data['trading_date'],
                            int(stock_data['trading_date'].strftime('%s')),
                            datetime.combine(stock_data['trading_date'], datetime.min.time()),
                            int(datetime.combine(stock_data['trading_date'], datetime.min.time()).timestamp()),
                            stock_data['open_price'], stock_data['high_price'], 
                            stock_data['low_price'], stock_data['close_price'], stock_data['volume'],
                            stock_data['adjusted_close'], stock_data['split_factor'], 
                            stock_data['dividend_amount'], stock_data['data_source'], stock_data['raw_data_hash']
                        ))
                        
                        if cursor.rowcount > 0:
                            records_inserted += 1
                        else:
                            records_updated += 1
                        
                        # Insert job detail record
                        processing_time_ms = int((time.time() - instrument_start_time) * 1000)
                        cursor.execute(f"""
                        INSERT INTO {target_schema}.etl_job_details (
                            job_id, instrument_id, symbol, operation, 
                            date_processed, date_processed_epoch, records_count,
                            processing_time_ms
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            job_id, instrument_id, stock_data['symbol'], 'upsert',
                            stock_data['trading_date'], int(stock_data['trading_date'].strftime('%s')),
                            1, processing_time_ms
                        ))
                        
                    except Exception as e:
                        records_failed += 1
                        logger.error(f"Failed to process stock {stock_data['symbol']}: {e}")
                        
                        # Insert error detail
                        cursor.execute(f"""
                        INSERT INTO {target_schema}.etl_job_details (
                            job_id, symbol, operation, 
                            date_processed, date_processed_epoch, records_count,
                            error_details
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            job_id, stock_data['symbol'], 'failed',
                            stock_data['trading_date'], int(stock_data['trading_date'].strftime('%s')),
                            0, str(e)
                        ))
                
                # Process index data (similar pattern)
                for index_data in extract_results['data']['indices']:
                    try:
                        instrument_start_time = time.time()
                        
                        # Get index instrument and insert price data
                        cursor.execute(f"""
                        SELECT bi.id, i.id FROM {target_schema}.base_instruments bi
                        JOIN {target_schema}.indices i ON bi.id = i.instrument_id
                        WHERE bi.symbol = %s AND bi.instrument_type = 'index'
                        """, (index_data['symbol'],))
                        
                        result = cursor.fetchone()
                        if not result:
                            logger.warning(f"Index {index_data['symbol']} not found - skipping")
                            continue
                        
                        instrument_id, index_id = result
                        
                        # Insert index price data
                        cursor.execute(f"""
                        INSERT INTO {target_schema}.index_prices (
                            index_id, trading_date_local, trading_date_utc, trading_date_epoch,
                            trading_datetime_utc, trading_datetime_epoch,
                            open_value, high_value, low_value, close_value,
                            trading_volume, total_market_cap, constituents_traded,
                            data_source, raw_data_hash
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) ON CONFLICT (index_id, trading_date_local)
                        DO UPDATE SET 
                            open_value = EXCLUDED.open_value,
                            high_value = EXCLUDED.high_value,
                            low_value = EXCLUDED.low_value,
                            close_value = EXCLUDED.close_value,
                            trading_volume = EXCLUDED.trading_volume,
                            total_market_cap = EXCLUDED.total_market_cap,
                            raw_data_hash = EXCLUDED.raw_data_hash
                        """, (
                            index_id, index_data['trading_date'], index_data['trading_date'],
                            int(index_data['trading_date'].strftime('%s')),
                            datetime.combine(index_data['trading_date'], datetime.min.time()),
                            int(datetime.combine(index_data['trading_date'], datetime.min.time()).timestamp()),
                            index_data['open_value'], index_data['high_value'],
                            index_data['low_value'], index_data['close_value'],
                            index_data['trading_volume'], index_data['total_market_cap'],
                            index_data['constituents_traded'], index_data['data_source'], 
                            index_data['raw_data_hash']
                        ))
                        
                        if cursor.rowcount > 0:
                            records_inserted += 1
                        else:
                            records_updated += 1
                        
                        # Insert job detail record
                        processing_time_ms = int((time.time() - instrument_start_time) * 1000)
                        cursor.execute(f"""
                        INSERT INTO {target_schema}.etl_job_details (
                            job_id, instrument_id, symbol, operation,
                            date_processed, date_processed_epoch, records_count,
                            processing_time_ms
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            job_id, instrument_id, index_data['symbol'], 'upsert',
                            index_data['trading_date'], int(index_data['trading_date'].strftime('%s')),
                            1, processing_time_ms
                        ))
                        
                    except Exception as e:
                        records_failed += 1
                        logger.error(f"Failed to process index {index_data['symbol']}: {e}")
                
                conn.commit()
        
        total_processing_time = int((time.time() - start_time) * 1000)
        total_processed = records_inserted + records_updated + records_failed
        success_rate = ((records_inserted + records_updated) / total_processed * 100) if total_processed > 0 else 0
        
        # Update ETL job with results
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                UPDATE {target_schema}.etl_jobs 
                SET records_processed = %s,
                    records_inserted = %s, 
                    records_updated = %s,
                    records_failed = %s
                WHERE id = %s
                """, (total_processed, records_inserted, records_updated, records_failed, job_id))
                conn.commit()
        
        results = {
            'total_processed': total_processed,
            'records_inserted': records_inserted,
            'records_updated': records_updated,
            'total_failed': records_failed,
            'success_rate': success_rate,
            'processing_time_ms': total_processing_time,
            'job_id': job_id,
            'schema': target_schema
        }
        
        logger.info(f"Data loading completed: {records_inserted} inserted, {records_updated} updated, {records_failed} failed")
        return results
        
    except Exception as e:
        logger.error(f"Data loading failed: {e}")
        raise


def validate_data_quality(**context) -> Dict[str, Any]:
    """
    Perform comprehensive data quality validation with detailed metrics.
    
    Returns:
        Validation results
    """
    logger = ETLLogger('data_validation').get_logger()
    
    try:
        # Get context
        job_id = context['task_instance'].xcom_pull(task_ids='create_etl_job')
        load_results = context['task_instance'].xcom_pull(task_ids='load_data')
        target_schema = get_schema_from_context(context)
        
        # Skip validation if disabled
        if not context['params'].get('enable_validation', True):
            logger.info("Data validation disabled - skipping")
            return {'validation_skipped': True}
        
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        validation_results = {
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'metrics': []
        }
        
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                # Get target date
                target_date = context['task_instance'].xcom_pull(
                    task_ids='check_prerequisites', 
                    key='execution_config'
                )['target_date']
                
                # Data quality checks
                quality_checks = [
                    {
                        'name': 'price_gap_check',
                        'query': f"""
                        SELECT bi.id, bi.symbol, 
                               ABS(sp.close_price - LAG(sp.close_price) OVER (PARTITION BY sp.stock_id ORDER BY sp.trading_date_local)) / 
                               LAG(sp.close_price) OVER (PARTITION BY sp.stock_id ORDER BY sp.trading_date_local) as price_gap
                        FROM {target_schema}.stock_prices sp
                        JOIN {target_schema}.stocks s ON sp.stock_id = s.id
                        JOIN {target_schema}.base_instruments bi ON s.instrument_id = bi.id
                        WHERE sp.trading_date_local = %s
                        """,
                        'threshold_max': 0.20,  # 20% max price gap
                        'description': 'Check for unusual price gaps between trading sessions'
                    },
                    {
                        'name': 'ohlc_consistency',
                        'query': f"""
                        SELECT bi.id, bi.symbol,
                               CASE WHEN sp.high_price >= sp.open_price AND sp.high_price >= sp.close_price AND
                                         sp.low_price <= sp.open_price AND sp.low_price <= sp.close_price 
                                    THEN 1.0 ELSE 0.0 END as ohlc_valid
                        FROM {target_schema}.stock_prices sp
                        JOIN {target_schema}.stocks s ON sp.stock_id = s.id
                        JOIN {target_schema}.base_instruments bi ON s.instrument_id = bi.id
                        WHERE sp.trading_date_local = %s
                        """,
                        'threshold_min': 1.0,  # Must be 1.0 (valid)
                        'description': 'Validate OHLC price relationships'
                    },
                    {
                        'name': 'volume_consistency',
                        'query': f"""
                        SELECT bi.id, bi.symbol, sp.volume
                        FROM {target_schema}.stock_prices sp
                        JOIN {target_schema}.stocks s ON sp.stock_id = s.id
                        JOIN {target_schema}.base_instruments bi ON s.instrument_id = bi.id
                        WHERE sp.trading_date_local = %s AND sp.volume > 0
                        """,
                        'threshold_min': 1.0,  # Volume must be positive
                        'description': 'Check for reasonable trading volumes'
                    }
                ]
                
                for check in quality_checks:
                    try:
                        cursor.execute(check['query'], (target_date,))
                        results = cursor.fetchall()
                        
                        for result in results:
                            instrument_id, symbol, metric_value = result
                            
                            # Determine if metric passes validation
                            is_valid = True
                            severity = 'info'
                            
                            if check.get('threshold_min') and metric_value < check['threshold_min']:
                                is_valid = False
                                severity = 'warning'
                            elif check.get('threshold_max') and metric_value > check['threshold_max']:
                                is_valid = False
                                severity = 'warning' if metric_value < check['threshold_max'] * 1.5 else 'error'
                            
                            # Insert data quality metric
                            cursor.execute(f"""
                            INSERT INTO {target_schema}.data_quality_metrics (
                                job_id, instrument_id, instrument_type, metric_date, metric_date_epoch,
                                metric_name, metric_value, threshold_min, threshold_max,
                                is_valid, severity, description
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                job_id, instrument_id, 'stock', target_date, int(target_date.strftime('%s')),
                                check['name'], metric_value, check.get('threshold_min'), check.get('threshold_max'),
                                is_valid, severity, check['description']
                            ))
                            
                            validation_results['total_checks'] += 1
                            if is_valid:
                                validation_results['passed_checks'] += 1
                            else:
                                validation_results['failed_checks'] += 1
                            
                            validation_results['metrics'].append({
                                'instrument': symbol,
                                'metric': check['name'],
                                'value': float(metric_value),
                                'valid': is_valid,
                                'severity': severity
                            })
                    
                    except Exception as e:
                        logger.error(f"Validation check {check['name']} failed: {e}")
                        validation_results['failed_checks'] += 1
                
                conn.commit()
        
        logger.info(f"Data validation completed: {validation_results['passed_checks']}/{validation_results['total_checks']} checks passed")
        return validation_results
        
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        raise


def finalize_etl_session(**context) -> None:
    """
    Finalize ETL session with comprehensive job completion tracking.
    """
    logger = ETLLogger('etl_finalization').get_logger()
    
    try:
        # Get all results
        job_id = context['task_instance'].xcom_pull(task_ids='create_etl_job')
        load_results = context['task_instance'].xcom_pull(task_ids='load_data')
        validation_results = context['task_instance'].xcom_pull(task_ids='validate_data_quality')
        target_schema = get_schema_from_context(context)
        
        # Calculate final job status
        final_status = 'completed'
        if load_results.get('total_failed', 0) > 0:
            if load_results.get('success_rate', 0) < 50:
                final_status = 'failed'
            else:
                final_status = 'completed'  # Partial success
        
        # Update ETL job with final results
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                completed_at = datetime.now()
                
                # Get job start time for duration calculation
                cursor.execute(f"""
                SELECT started_at FROM {target_schema}.etl_jobs WHERE id = %s
                """, (job_id,))
                
                started_at = cursor.fetchone()[0]
                duration_seconds = int((completed_at - started_at).total_seconds())
                
                # Update job record
                cursor.execute(f"""
                UPDATE {target_schema}.etl_jobs 
                SET status = %s,
                    completed_at = %s,
                    completed_at_epoch = %s,
                    duration_seconds = %s
                WHERE id = %s
                """, (
                    final_status, completed_at, int(completed_at.timestamp()),
                    duration_seconds, job_id
                ))
                
                conn.commit()
        
        # Create final summary
        final_summary = {
            'job_id': job_id,
            'status': final_status,
            'execution_date': context['ds'],
            'schema': target_schema,
            'duration_seconds': duration_seconds,
            'total_processed': load_results.get('total_processed', 0),
            'total_inserted': load_results.get('records_inserted', 0),
            'total_updated': load_results.get('records_updated', 0),
            'total_failed': load_results.get('total_failed', 0),
            'success_rate': load_results.get('success_rate', 0),
            'validation_passed': validation_results.get('passed_checks', 0),
            'validation_failed': validation_results.get('failed_checks', 0),
            'completed_at': completed_at.isoformat()
        }
        
        # Log execution summary
        execution_config = context['task_instance'].xcom_pull(
            task_ids='check_prerequisites', 
            key='execution_config'
        )
        log_execution_summary(execution_config, final_summary)
        
        # Store final summary in XCom
        context['task_instance'].xcom_push(key='final_summary', value=final_summary)
        
        logger.info(f"ETL session completed: Job {job_id} finished with status '{final_status}'")
        
    except Exception as e:
        logger.error(f"Error in ETL finalization: {e}")
        # Mark job as failed
        if job_id:
            postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
            with postgres_hook.get_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                    UPDATE {target_schema}.etl_jobs 
                    SET status = 'failed', error_message = %s 
                    WHERE id = %s
                    """, (str(e), job_id))
                    conn.commit()
        raise


# Task definitions
check_prerequisites_task = BranchPythonOperator(
    task_id='check_prerequisites',
    python_callable=check_execution_prerequisites,
    dag=dag
)

skip_execution_task = EmptyOperator(
    task_id='skip_execution',
    dag=dag
)

proceed_task = EmptyOperator(
    task_id='proceed_with_etl',
    dag=dag
)

create_etl_job_task = PythonOperator(
    task_id='create_etl_job',
    python_callable=create_etl_job_record,
    dag=dag
)

extract_transform_task = PythonOperator(
    task_id='extract_and_transform',
    python_callable=extract_and_transform_data,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data_to_database,
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    dag=dag
)

finalize_task = PythonOperator(
    task_id='finalize_etl_session',
    python_callable=finalize_etl_session,
    trigger_rule='none_failed_min_one_success',  # Run even if validation fails
    dag=dag
)

# Task dependencies
check_prerequisites_task >> [skip_execution_task, proceed_task]
proceed_task >> create_etl_job_task >> extract_transform_task >> load_task >> validate_task >> finalize_task