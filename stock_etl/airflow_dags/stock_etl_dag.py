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
from typing import Dict, Any, List, Tuple
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

from stock_etl.utils.dag_utils import (
    determine_execution_mode, 
    should_skip_execution, 
    get_schema_from_context,
    log_execution_summary,
    ETLLogger
)
from stock_etl.utils.polish_trading_calendar import polish_calendar

# Import ETL core modules for authentic data extraction
try:
    from stock_etl.data.stooq_extractor import StooqExtractor
    from stock_etl.database.operations import DatabaseOperations
    from stock_etl.core.database import get_database_manager
    from stock_etl.core.models import StooqRecord, InstrumentType
    STOOQ_AVAILABLE = True
except ImportError as e:
    # Raise error instead of fallback for non-dev environments
    STOOQ_AVAILABLE = False
    IMPORT_ERROR = str(e)


# Environment configurations for dynamic DAG generation
ENVIRONMENTS = {
    'dev': {
        'schema': 'dev_stock_data',
        'description': 'Development stock data ETL pipeline',
        'schedule': None,  # Manual triggering for development
        'tags': ['stock-data', 'etl', 'development'],
        'retries': 1,
        'catchup': False
    },
    'test': {
        'schema': 'test_stock_data', 
        'description': 'Test stock data ETL pipeline',
        'schedule': None,  # Manual triggering for testing
        'tags': ['stock-data', 'etl', 'testing'],
        'retries': 1,
        'catchup': False
    },
    'prod': {
        'schema': 'prod_stock_data',
        'description': 'Production stock data ETL pipeline',
        'schedule': '0 18 * * 1-5',  # Run at 6 PM on weekdays
        'tags': ['stock-data', 'etl', 'production'],
        'retries': 2,
        'catchup': True
    }
}

def create_dag(environment_name, environment_config):
    """
    Create a DAG for a specific environment using dynamic configuration.
    """
    
    # DAG Configuration
    default_args = {
        'owner': 'stock-etl',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': environment_config['retries'],
        'retry_delay': timedelta(minutes=5),
        'catchup': environment_config['catchup'],
    }

    # Create environment-specific DAG
    dag = DAG(
        f'{environment_name}_stock_etl_pipeline',
        default_args=default_args,
        description=environment_config['description'],
        schedule=environment_config['schedule'],
        max_active_runs=1,  # Prevent concurrent runs
        tags=environment_config['tags'],
        params={
            'schema': environment_config['schema'],
            'mode': 'incremental', 
            'instruments': 'all',
            'data_source': 'stooq',
            'enable_validation': True,
            'batch_size': 50,
            'environment': environment_name  # Add environment identifier
        }
    )

    # Task definitions inside the DAG function
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
        trigger_rule='none_failed_min_one_success',
        dag=dag
    )

    # Task dependencies
    check_prerequisites_task >> [skip_execution_task, proceed_task]
    proceed_task >> create_etl_job_task >> extract_transform_task >> load_task >> validate_task >> finalize_task
    
    return dag


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
        
        # Get schema from DAG params (environment-specific)
        target_schema = context['params']['schema']
        
        # Create job metadata
        job_metadata = {
            'airflow_context': {
                'dag_id': context['dag'].dag_id,
                'task_id': context['task'].task_id,
                'run_id': context['run_id'],
                'execution_date': context.get('ds'),
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
        # Get schema from DAG params (environment-specific)
        target_schema = context['params']['schema']
        environment = context['params']['environment']
        
        # Get execution parameters
        target_date = execution_config['target_date']
        instruments = context['params'].get('instruments', 'all')
        
        logger.info(f"Extracting data for {target_date} - environment: {environment} - instruments: {instruments}")
        
        # Use mock data for development, authentic Stooq data for test/prod
        if environment == 'dev':
            logger.info("Using mock data for development environment")
            extracted_data = _extract_mock_data(target_date, logger)
        else:
            logger.info(f"Using authentic Stooq data for {environment} environment")
            if not STOOQ_AVAILABLE:
                error_msg = f"Stooq modules not available for {environment} environment: {IMPORT_ERROR}"
                logger.error(error_msg)
                raise ImportError(error_msg)
            extracted_data = _extract_stooq_data(target_date, target_schema, logger, context)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Update data source statistics
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        # Data source tracking is now handled via etl_jobs and etl_job_details tables
        logger.info("Data source tracking handled via ETL job metadata")
        
        results = {
            'data': extracted_data,
            'total_records': len(extracted_data['stocks']) + len(extracted_data['indices']),
            'processing_time_ms': processing_time_ms,
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


def ensure_reference_data_exists(cursor, target_schema, logger):
    """Ensure required reference data exists for ETL operations."""
    
    # Check and create country
    cursor.execute(f"SELECT COUNT(*) FROM {target_schema}.countries WHERE iso_code = 'POL'")
    if cursor.fetchone()[0] == 0:
        logger.info("Creating Poland country reference data")
        cursor.execute(f"""
            INSERT INTO {target_schema}.countries (name, iso_code, currency_code, timezone) 
            VALUES ('Poland', 'POL', 'PLN', 'Europe/Warsaw')
        """)
    
    # Check and create exchange
    cursor.execute(f"SELECT COUNT(*) FROM {target_schema}.exchanges WHERE mic_code = 'XWAR'")
    if cursor.fetchone()[0] == 0:
        logger.info("Creating WSE exchange reference data")
        cursor.execute(f"""
            INSERT INTO {target_schema}.exchanges (name, mic_code, country_id, timezone, market_open, market_close, is_active)
            VALUES ('Warsaw Stock Exchange', 'XWAR', 
                    (SELECT id FROM {target_schema}.countries WHERE iso_code = 'POL'),
                    'Europe/Warsaw', '09:00:00', '17:00:00', TRUE)
        """)
    
    # Check and create basic sectors
    cursor.execute(f"SELECT COUNT(*) FROM {target_schema}.sectors WHERE code IN ('FINS', 'ENRG')")
    if cursor.fetchone()[0] < 2:
        logger.info("Creating basic sector reference data")
        cursor.execute(f"""
            INSERT INTO {target_schema}.sectors (name, code, description) VALUES 
            ('Financial Services', 'FINS', 'Banks, insurance, financial services'),
            ('Energy', 'ENRG', 'Oil, gas, renewable energy')
            ON CONFLICT (code) DO NOTHING
        """)

def load_data_to_database(**context) -> Dict[str, Any]:
    """
    Load transformed data with incremental commits per instrument.
    Each instrument (stock/index) is processed and committed individually,
    providing better fault tolerance and immediate visibility of progress.
    
    Returns:
        Load operation results
    """
    logger = ETLLogger('data_load').get_logger()
    start_time = time.time()
    
    try:
        # Get context data
        job_id = context['task_instance'].xcom_pull(task_ids='create_etl_job')
        extract_results = context['task_instance'].xcom_pull(task_ids='extract_and_transform')
        # Get schema from DAG params (environment-specific)
        target_schema = context['params']['schema']
        
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        records_inserted = 0
        records_updated = 0
        records_failed = 0
        
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                # Ensure required reference data exists
                ensure_reference_data_exists(cursor, target_schema, logger)
                conn.commit()  # Commit reference data before processing
                
                # Process stock data with incremental commits
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
                            # Create missing instrument automatically for ETL
                            logger.info(f"Creating missing instrument {stock_data['symbol']}")
                            
                            # Get WSE exchange ID (assuming it exists)
                            cursor.execute(f"SELECT id FROM {target_schema}.exchanges WHERE mic_code = 'XWAR' LIMIT 1")
                            exchange_result = cursor.fetchone()
                            exchange_id = exchange_result[0] if exchange_result else 1  # Default to 1 if not found
                            
                            # Insert base instrument
                            cursor.execute(f"""
                            INSERT INTO {target_schema}.base_instruments 
                            (symbol, name, instrument_type, exchange_id, currency, is_active)
                            VALUES (%s, %s, 'stock', %s, 'PLN', true)
                            RETURNING id
                            """, (stock_data['symbol'], f"{stock_data['symbol']} Stock", exchange_id))
                            
                            instrument_id = cursor.fetchone()[0]
                        else:
                            instrument_id = result[0]
                        
                        # Get or create stock record (using instrument_id as PK in unified design)
                        cursor.execute(f"""
                        SELECT instrument_id FROM {target_schema}.stocks 
                        WHERE instrument_id = %s
                        """, (instrument_id,))
                        
                        stock_result = cursor.fetchone()
                        if not stock_result:
                            # Create missing stock record
                            logger.info(f"Creating missing stock record for {stock_data['symbol']}")
                            cursor.execute(f"""
                            INSERT INTO {target_schema}.stocks 
                            (instrument_id, company_name, stock_type)
                            VALUES (%s, %s, 'common')
                            """, (instrument_id, f"{stock_data['symbol']} Company"))
                            
                            # In unified design, stock_id equals instrument_id
                            stock_id = instrument_id
                        else:
                            # stock_result[0] is instrument_id, which is the stock_id in unified design
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
                            job_id, instrument_id, symbol, instrument_type,
                            target_date, target_date_epoch, records_processed,
                            duration_milliseconds, processing_order, data_source, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            job_id, instrument_id, stock_data['symbol'], 'stock',
                            stock_data['trading_date'], int(stock_data['trading_date'].strftime('%s')),
                            1, processing_time_ms, 1, 'stooq', 'completed'
                        ))
                        
                        # Commit after each stock instrument is processed
                        conn.commit()
                        logger.debug(f"Successfully processed and committed stock {stock_data['symbol']}")
                        
                    except Exception as e:
                        records_failed += 1
                        logger.error(f"Failed to process stock {stock_data['symbol']}: {e}")
                        
                        # Rollback current transaction for this instrument
                        conn.rollback()
                        
                        # Insert error detail in a separate transaction
                        try:
                            cursor.execute(f"""
                            INSERT INTO {target_schema}.etl_job_details (
                                job_id, symbol, instrument_type,
                                target_date, target_date_epoch, records_processed,
                                error_message, processing_order, data_source, status
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                job_id, stock_data['symbol'], 'stock',
                                stock_data['trading_date'], int(stock_data['trading_date'].strftime('%s')),
                                0, str(e), 1, 'stooq', 'failed'
                            ))
                            conn.commit()  # Commit error record
                        except Exception as error_log_ex:
                            logger.error(f"Failed to log error for {stock_data['symbol']}: {error_log_ex}")
                            conn.rollback()
                
                # Process index data with incremental commits
                for index_data in extract_results['data']['indices']:
                    try:
                        instrument_start_time = time.time()
                        
                        # Get or create index instrument (unified ID design)
                        cursor.execute(f"""
                        SELECT bi.id FROM {target_schema}.base_instruments bi
                        JOIN {target_schema}.indices i ON bi.id = i.instrument_id
                        WHERE bi.symbol = %s AND bi.instrument_type = 'index'
                        """, (index_data['symbol'],))
                        
                        result = cursor.fetchone()
                        if not result:
                            # Create missing index automatically for ETL
                            logger.info(f"Creating missing index {index_data['symbol']}")
                            
                            # Get WSE exchange ID (assuming it exists)
                            cursor.execute(f"SELECT id FROM {target_schema}.exchanges WHERE mic_code = 'XWAR' LIMIT 1")
                            exchange_result = cursor.fetchone()
                            exchange_id = exchange_result[0] if exchange_result else 1  # Default to 1 if not found
                            
                            # Insert base instrument
                            cursor.execute(f"""
                            INSERT INTO {target_schema}.base_instruments 
                            (symbol, name, instrument_type, exchange_id, currency, is_active)
                            VALUES (%s, %s, 'index', %s, 'PLN', true)
                            RETURNING id
                            """, (index_data['symbol'], f"{index_data['symbol']} Index", exchange_id))
                            
                            instrument_id = cursor.fetchone()[0]
                            
                            # Create index record
                            logger.info(f"Creating missing index record for {index_data['symbol']}")
                            cursor.execute(f"""
                            INSERT INTO {target_schema}.indices 
                            (instrument_id, methodology, base_value, base_date, index_family)
                            VALUES (%s, 'market_cap_weighted', 1000.0, '2000-01-01', 'WSE')
                            """, (instrument_id,))
                            
                            # In unified design, index_id equals instrument_id
                            index_id = instrument_id
                        else:
                            # In unified design, instrument_id and index_id are the same
                            instrument_id = result[0]
                            index_id = instrument_id
                        
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
                            job_id, instrument_id, symbol, instrument_type,
                            target_date, target_date_epoch, records_processed,
                            duration_milliseconds, processing_order, data_source, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            job_id, instrument_id, index_data['symbol'], 'index',
                            index_data['trading_date'], int(index_data['trading_date'].strftime('%s')),
                            1, processing_time_ms, 2, 'stooq', 'completed'
                        ))
                        
                        # Commit after each index instrument is processed
                        conn.commit()
                        logger.debug(f"Successfully processed and committed index {index_data['symbol']}")
                        
                    except Exception as e:
                        records_failed += 1
                        logger.error(f"Failed to process index {index_data['symbol']}: {e}")
                        
                        # Rollback current transaction for this instrument
                        conn.rollback()
                        
                        # Insert error detail in a separate transaction
                        try:
                            cursor.execute(f"""
                            INSERT INTO {target_schema}.etl_job_details (
                                job_id, symbol, instrument_type,
                                target_date, target_date_epoch, records_processed,
                                error_message, processing_order, data_source, status
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                job_id, index_data['symbol'], 'index',
                                index_data['trading_date'], int(index_data['trading_date'].strftime('%s')),
                                0, str(e), 2, 'stooq', 'failed'
                            ))
                            conn.commit()  # Commit error record
                        except Exception as error_log_ex:
                            logger.error(f"Failed to log error for {index_data['symbol']}: {error_log_ex}")
                            conn.rollback()
        
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
        # Get schema from DAG params (environment-specific)
        target_schema = context['params']['schema']
        
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
                               COALESCE(
                                   ABS(sp.close_price - LAG(sp.close_price) OVER (PARTITION BY sp.stock_id ORDER BY sp.trading_date_local)) / 
                                   NULLIF(LAG(sp.close_price) OVER (PARTITION BY sp.stock_id ORDER BY sp.trading_date_local), 0),
                                   0.0
                               ) as price_gap
                        FROM {target_schema}.stock_prices sp
                        JOIN {target_schema}.base_instruments bi ON sp.stock_id = bi.id
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
                        JOIN {target_schema}.base_instruments bi ON sp.stock_id = bi.id
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
                        JOIN {target_schema}.base_instruments bi ON sp.stock_id = bi.id
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
                            
                            # Insert data quality metric (using actual schema columns)
                            threshold_value = check.get('threshold_max') or check.get('threshold_min')
                            cursor.execute(f"""
                            INSERT INTO {target_schema}.data_quality_metrics (
                                job_id, instrument_id, metric_name, metric_value, 
                                threshold_value, is_valid, severity, description
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                job_id, instrument_id, check['name'], metric_value,
                                threshold_value, is_valid, severity, check['description']
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
        load_results = context['task_instance'].xcom_pull(task_ids='load_data') or {}
        validation_results = context['task_instance'].xcom_pull(task_ids='validate_data_quality') or {}
        # Get schema from DAG params (environment-specific)
        target_schema = context['params']['schema']
        
        # Calculate final job status
        final_status = 'completed'
        if load_results.get('total_failed', 0) > 0:
            if load_results.get('success_rate', 0) < 50:
                final_status = 'failed'
            else:
                final_status = 'completed'  # Partial success
        
        # Update ETL job with final results (skip if testing without job_id)
        duration_seconds = 0
        if job_id:
            postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
            with postgres_hook.get_conn() as conn:
                with conn.cursor() as cursor:
                    # Use timezone-naive datetime to match database schema
                    completed_at = datetime.now()
                    if completed_at.tzinfo is not None:
                        completed_at = completed_at.replace(tzinfo=None)
                    
                    # Get job start time for duration calculation
                    cursor.execute(f"""
                    SELECT started_at FROM {target_schema}.etl_jobs WHERE id = %s
                    """, (job_id,))
                    
                    started_at = cursor.fetchone()[0]
                    # Ensure both datetimes are timezone-naive
                    if started_at.tzinfo is not None:
                        started_at = started_at.replace(tzinfo=None)
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
        else:
            logger.info("No job_id found - skipping database update (likely testing mode)")
            completed_at = datetime.now()
        
        # Create final summary
        final_summary = {
            'job_id': job_id,
            'status': final_status,
            'execution_date': context.get('ds'),
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
        ) or {}
        if execution_config:
            log_execution_summary(execution_config, final_summary)
        else:
            logger.info("No execution config found - skipping execution summary (likely testing mode)")
        
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


def _extract_mock_data(target_date, logger):
    """
    Extract mock data for development environment.
    """
    return {
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


def determine_extraction_strategy(symbol: str, instrument_type: str, target_schema: str, context: Dict[str, Any]) -> Tuple[str, str, int]:
    """
    Intelligent extraction strategy determination based on database state and context.
    
    Args:
        symbol: Stock/index symbol
        instrument_type: 'stock' or 'index'
        target_schema: Database schema to check
        context: Airflow task context
    
    Returns:
        Tuple of (strategy, reason, max_records_to_process)
        strategy: 'historical' | 'incremental'
        reason: Human-readable explanation
        max_records_to_process: Limit for historical processing
    """
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # Layer 1: Check explicit configuration override
    conf = context.get('dag_run', {}).conf if context.get('dag_run') else {}
    manual_conf = conf if conf else {}
    
    # Check for instrument-specific override
    instrument_overrides = manual_conf.get('instruments', {})
    if isinstance(instrument_overrides, dict) and symbol in instrument_overrides:
        override_mode = instrument_overrides[symbol]
        if override_mode in ['historical', 'incremental']:
            return override_mode, f'Manual override: {symbol} → {override_mode}', 1000
    
    # Check for global extraction mode override
    global_mode = manual_conf.get('extraction_mode', 'smart')
    if global_mode == 'full_backfill':
        return 'historical', 'UNLIMITED BACKFILL: All available historical data', -1  # -1 = unlimited
    elif global_mode == 'historical':
        return 'historical', 'Global historical mode override', 1000
    elif global_mode == 'incremental':
        return 'incremental', 'Global incremental mode override', 1
    
    # Layer 2: Database state analysis
    try:
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                if instrument_type == 'stock':
                    # Check stock price data
                    cursor.execute(f"""
                        SELECT COUNT(*) as record_count, 
                               MIN(trading_date) as earliest_date,
                               MAX(trading_date) as latest_date,
                               MAX(trading_date) < (CURRENT_DATE - INTERVAL '7 days') as is_stale
                        FROM {target_schema}.stock_prices sp 
                        JOIN {target_schema}.base_instruments bi ON sp.stock_id = bi.id 
                        WHERE bi.symbol = %s
                    """, (symbol,))
                else:
                    # Check index price data
                    cursor.execute(f"""
                        SELECT COUNT(*) as record_count,
                               MIN(trading_date) as earliest_date, 
                               MAX(trading_date) as latest_date,
                               MAX(trading_date) < (CURRENT_DATE - INTERVAL '7 days') as is_stale
                        FROM {target_schema}.index_prices ip
                        JOIN {target_schema}.base_instruments bi ON ip.index_id = bi.id  
                        WHERE bi.symbol = %s
                    """, (symbol,))
                
                result = cursor.fetchone()
                if result:
                    record_count, earliest_date, latest_date, is_stale = result
                    
                    # Decision logic based on database state
                    if record_count == 0:
                        return 'historical', f'New instrument: no existing data for {symbol}', 1000
                    
                    if is_stale:
                        days_stale = (datetime.now().date() - latest_date).days if latest_date else 999
                        return 'historical', f'Stale data: {symbol} last updated {days_stale} days ago', 500
                    
                    # Check for significant data gaps (more than 30 days)
                    if latest_date and record_count < 30:  # Less than a month of data
                        return 'historical', f'Sparse data: only {record_count} records for {symbol}', 1000
                    
                    # Data looks current - incremental update
                    return 'incremental', f'Current data: {symbol} last updated {latest_date}', 1
                
    except Exception as e:
        # Fallback to execution mode context if database check fails
        pass
    
    # Layer 3: DAG execution mode fallback
    mode, config = determine_execution_mode(context)
    if mode == 'backfill':
        return 'historical', f'Backfill execution mode detected', 1000
    
    # Layer 4: Default to incremental for safety
    return 'incremental', f'Default incremental mode for {symbol}', 1


def _extract_stooq_data(target_date, target_schema, logger, context):
    """
    Extract authentic data from Stooq API with intelligent historical/incremental processing.
    
    Args:
        target_date: Target date for extraction
        target_schema: Database schema
        logger: Logger instance
        context: Airflow task context for strategy determination
    """
    try:
        # Initialize the StooqExtractor
        extractor = StooqExtractor()
        
        # Define sample symbols (these should be present in the target schema)
        sample_symbols = {
            'stocks': ['XTB', 'CDR', 'ELT', 'DVL', 'BDX', 'PLW', 'KTY', 'PZU', 'RBW', 'GPW'],
            'indices': ['WIG', 'WIG20', 'MWIG40', 'SWIG80']
        }
        
        extracted_data = {'stocks': [], 'indices': []}
        
        # Extract stock data with intelligent historical/incremental processing
        for symbol in sample_symbols['stocks']:
            try:
                # Determine extraction strategy for this specific instrument
                strategy, reason, max_records = determine_extraction_strategy(
                    symbol, 'stock', target_schema, context
                )
                
                logger.info(f"Extracting data for stock {symbol}: {strategy} mode ({reason})")
                stock_data = extractor.extract_symbol(symbol, InstrumentType.STOCK)
                
                if stock_data and len(stock_data) > 0:
                    # Process records based on strategy
                    if strategy == 'historical':
                        # Process multiple records (unlimited if max_records = -1)
                        if max_records == -1:
                            records_to_process = stock_data  # ALL records - unlimited
                            logger.info(f"Processing ALL {len(records_to_process)} historical records for {symbol} (UNLIMITED BACKFILL)")
                        else:
                            records_to_process = stock_data[-max_records:] if len(stock_data) > max_records else stock_data
                            logger.info(f"Processing {len(records_to_process)} historical records for {symbol}")
                        
                        for record in records_to_process:
                            extracted_data['stocks'].append({
                                'symbol': symbol,
                                'trading_date': record.trading_date,
                                'open_price': record.open_price,
                                'high_price': record.high_price,
                                'low_price': record.low_price,
                                'close_price': record.close_price,
                                'volume': record.volume,
                                'adjusted_close': record.close_price,
                                'split_factor': 1.0,
                                'dividend_amount': 0.0,
                                'data_source': 'stooq',
                                'raw_data_hash': record.calculate_hash()
                            })
                    else:
                        # Incremental: process only the latest record
                        latest_record = stock_data[-1]
                        extracted_data['stocks'].append({
                            'symbol': symbol,
                            'trading_date': latest_record.trading_date,
                            'open_price': latest_record.open_price,
                            'high_price': latest_record.high_price,
                            'low_price': latest_record.low_price,
                            'close_price': latest_record.close_price,
                            'volume': latest_record.volume,
                            'adjusted_close': latest_record.close_price,
                            'split_factor': 1.0,
                            'dividend_amount': 0.0,
                            'data_source': 'stooq',
                            'raw_data_hash': latest_record.calculate_hash()
                        })
                    
                    logger.info(f"Successfully extracted {strategy} data for {symbol}")
                else:
                    logger.warning(f"No data found for stock {symbol}")
            except Exception as e:
                logger.error(f"Failed to extract data for stock {symbol}: {e}")
        
        # Extract index data with intelligent historical/incremental processing
        for symbol in sample_symbols['indices']:
            try:
                # Determine extraction strategy for this specific index
                strategy, reason, max_records = determine_extraction_strategy(
                    symbol, 'index', target_schema, context
                )
                
                logger.info(f"Extracting data for index {symbol}: {strategy} mode ({reason})")
                index_data = extractor.extract_symbol(symbol, InstrumentType.INDEX)
                
                if index_data and len(index_data) > 0:
                    # Process records based on strategy
                    if strategy == 'historical':
                        # Process multiple records (unlimited if max_records = -1)
                        if max_records == -1:
                            records_to_process = index_data  # ALL records - unlimited
                            logger.info(f"Processing ALL {len(records_to_process)} historical records for {symbol} (UNLIMITED BACKFILL)")
                        else:
                            records_to_process = index_data[-max_records:] if len(index_data) > max_records else index_data
                            logger.info(f"Processing {len(records_to_process)} historical records for {symbol}")
                        
                        for record in records_to_process:
                            extracted_data['indices'].append({
                                'symbol': symbol,
                                'trading_date': record.trading_date,
                                'open_value': record.open_price,
                                'high_value': record.high_price,
                                'low_value': record.low_price,
                                'close_value': record.close_price,
                                'trading_volume': record.volume,
                                'total_market_cap': 750000000000.0,  # Placeholder
                                'constituents_traded': 350,  # Placeholder
                                'data_source': 'stooq',
                                'raw_data_hash': record.calculate_hash()
                            })
                    else:
                        # Incremental: process only the latest record
                        latest_record = index_data[-1]
                        extracted_data['indices'].append({
                            'symbol': symbol,
                            'trading_date': latest_record.trading_date,
                            'open_value': latest_record.open_price,
                            'high_value': latest_record.high_price,
                            'low_value': latest_record.low_price,
                            'close_value': latest_record.close_price,
                            'trading_volume': latest_record.volume,
                            'total_market_cap': 750000000000.0,  # Placeholder
                            'constituents_traded': 350,  # Placeholder
                            'data_source': 'stooq',
                            'raw_data_hash': latest_record.calculate_hash()
                        })
                    
                    logger.info(f"Successfully extracted {strategy} data for {symbol}")
                else:
                    logger.warning(f"No data found for index {symbol}")
            except Exception as e:
                logger.error(f"Failed to extract data for index {symbol}: {e}")
        
        logger.info(f"Stooq extraction completed: {len(extracted_data['stocks'])} stocks, {len(extracted_data['indices'])} indices")
        return extracted_data
        
    except Exception as e:
        logger.error(f"Failed to extract Stooq data: {e}")
        raise Exception(f"Stooq data extraction failed: {e}") from e


# Generate DAGs for all environments
for env_name, env_config in ENVIRONMENTS.items():
    dag_id = f'{env_name}_stock_etl_pipeline'
    globals()[dag_id] = create_dag(env_name, env_config)