# ML DAG Multi-Environment Implementation Plan

## 🎯 **Project Goal**
Implement multi-environment ML DAGs following the same dynamic pattern as `stock_etl_dag.py` to support dev/test/prod deployment of machine learning pipelines.

## 📊 **Current State Analysis**

### ✅ **What's Working (test_stock_data)**
- ML pipeline successfully developed and tested in `test_stock_data` schema
- Schema template (`sql/schema_template.sql.j2`) already includes all ML tables
- ML DAG (`stock_etl/airflow_dags/stock_ml_dag.py`) works perfectly for test environment
- CPU optimization (2 cores per DAG) implemented and tested

### ❌ **Current Limitations**
1. **Hardcoded Schema References** in `stock_ml_dag.py`:
   ```python
   # Line 57: Hardcoded query
   SELECT DISTINCT symbol FROM test_stock_data.base_instruments
   
   # Line 122: Hardcoded target schema
   'target_schema': 'test_stock_data'
   
   # Line 453: Hardcoded instrument lookup
   test_stock_data.base_instruments
   ```

2. **Single Environment DAG**: Only generates DAGs for test environment
3. **No Production Schema**: `prod_stock_data` schema not initialized with ML tables
4. **Makefile Gaps**: Production environment setup doesn't include ML capabilities

## 🏗️ **Implementation Architecture**

### **Pattern to Follow: `stock_etl_dag.py`**
The ETL DAGs use this successful multi-environment pattern:

```python
# Environment configurations for dynamic DAG generation
ENVIRONMENTS = {
    'dev': {
        'schema': 'dev_stock_data',
        'description': 'Development stock data ETL pipeline',
        'schedule': None,  # Manual triggering
        'tags': ['stock-data', 'etl', 'development'],
        'retries': 1,
        'catchup': False
    },
    'test': {
        'schema': 'test_stock_data', 
        'description': 'Test stock data ETL pipeline',
        'schedule': None,  # Manual triggering
        'tags': ['stock-data', 'etl', 'testing'],
        'retries': 1,
        'catchup': False
    },
    'prod': {
        'schema': 'prod_stock_data',
        'description': 'Production stock data ETL pipeline',
        'schedule': '0 18 * * 1-5',  # 6 PM weekdays
        'tags': ['stock-data', 'etl', 'production'],
        'retries': 2,
        'catchup': True
    }
}

def create_dag(environment_name, environment_config):
    # Create environment-specific DAG
    dag = DAG(
        f'{environment_name}_stock_etl_pipeline',  # Dynamic DAG name
        # ... configuration
        params={
            'schema': environment_config['schema'],  # Dynamic schema
            'environment': environment_name  # Environment identifier
        }
    )

# Generate DAGs for all environments
for env_name, env_config in ENVIRONMENTS.items():
    dag_id = f'{env_name}_stock_etl_pipeline'
    globals()[dag_id] = create_dag(env_name, env_config)
```

## 🚀 **Implementation Plan**

### **Phase 1: Multi-Environment ML DAG Architecture**

#### **1.1 Create `stock_ml_dag_environments.py`** (New File)
Replace single-environment `stock_ml_dag.py` with multi-environment approach:

```python
# ML Environment configurations (following ETL pattern)
ML_ENVIRONMENTS = {
    'dev': {
        'schema': 'dev_stock_data',
        'description': 'Development ML pipeline for stock growth prediction',
        'schedule': None,  # Manual triggering for development
        'tags': ['ml-pipeline', 'stock-training', 'development', '7day-targets'],
        'retries': 1,
        'catchup': False,
        'is_paused': False,
        'grid_search_type': 'quick'
    },
    'test': {
        'schema': 'test_stock_data',
        'description': 'Test ML pipeline for stock growth prediction',
        'schedule': None,  # Manual triggering for testing
        'tags': ['ml-pipeline', 'stock-training', 'testing', '7day-targets'],
        'retries': 1,
        'catchup': False,
        'is_paused': False,  # Currently active
        'grid_search_type': 'comprehensive'
    },
    'prod': {
        'schema': 'prod_stock_data',
        'description': 'Production ML pipeline for stock growth prediction',
        'schedule': '0 18 * * 1-5',  # 6 PM weekdays (after market close)
        'tags': ['ml-pipeline', 'stock-training', 'production', '7day-targets'],
        'retries': 3,  # More retries for production
        'catchup': True,
        'is_paused': True,  # Paused until ready
        'grid_search_type': 'production'
    }
}

def create_ml_environment_dag(environment_name, environment_config):
    """Create ML DAGs for specific environment using dynamic configuration"""
    
    # Get active stock symbols from the environment-specific schema
    def get_environment_stock_symbols(target_schema):
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'''
                    SELECT DISTINCT symbol FROM {target_schema}.base_instruments
                    WHERE instrument_type='stock'
                    ORDER BY symbol
                ''')
                return [row[0] for row in cursor.fetchall()]
    
    # Generate per-stock DAGs for this environment
    target_schema = environment_config['schema']
    symbols = get_environment_stock_symbols(target_schema)
    
    environment_dags = {}
    
    for symbol in symbols:
        stock_key = symbol.lower()
        dag_id = f'{environment_name}_ml_pipeline_{stock_key}'
        
        # DAG Configuration
        default_args = {
            'owner': 'ml_pipeline',
            'depends_on_past': False,
            'start_date': datetime(2025, 8, 20),
            'email_on_failure': True,
            'email_on_retry': False,
            'retries': environment_config['retries'],
            'retry_delay': timedelta(minutes=15),
            'catchup': environment_config['catchup']
        }
        
        # Create environment-specific stock DAG
        dag = DAG(
            dag_id,
            default_args=default_args,
            description=f"{environment_config['description']} - {symbol}",
            schedule=environment_config['schedule'],
            max_active_runs=1,
            tags=environment_config['tags'] + [stock_key],
            is_paused_upon_creation=environment_config['is_paused'],
            params={
                'stock_symbol': symbol,
                'stock_key': stock_key,
                'target_schema': target_schema,  # Dynamic schema
                'environment': environment_name,  # Environment identifier
                'target_days': 7,
                'model_version_prefix': 'v2.1',
                'grid_search_type': environment_config['grid_search_type'],
                'web_application_ready': True
            }
        )
        
        # Tasks remain the same, but use dynamic schema from params
        # ... (task definitions)
        
        environment_dags[dag_id] = dag
    
    return environment_dags

# Generate DAGs for all environments
all_ml_dags = {}
for env_name, env_config in ML_ENVIRONMENTS.items():
    env_dags = create_ml_environment_dag(env_name, env_config)
    all_ml_dags.update(env_dags)
    
    # Register DAGs globally
    for dag_id, dag in env_dags.items():
        globals()[dag_id] = dag
```

#### **1.2 Schema-Configurable Database Operations**
Update all database operations to use dynamic schema:

```python
# Before (hardcoded)
SELECT DISTINCT symbol FROM test_stock_data.base_instruments

# After (configurable)
target_schema = context['params']['target_schema']
SELECT DISTINCT symbol FROM {target_schema}.base_instruments
```

**Key Changes Required:**
- `get_active_stock_symbols()`: Use parameterized schema
- `create_ml_etl_job()`: Dynamic schema in SQL queries
- `train_ml_model()`: Schema-aware database operations
- `finalize_ml_training()`: Environment-aware finalization

### **Phase 2: Infrastructure & Makefile Updates**

#### **2.1 Update Makefile for Production ML Support**

```makefile
# Add production schema initialization with ML tables
init-prod:
	@echo "🚀 Initializing production environment (prod_stock_data schema with ML tables)..."
	uv run python -m stock_etl.cli database init-prod
	@echo "✅ Production schema initialized with complete ML pipeline support"
	@echo "   - ETL tables: ✅"
	@echo "   - ML tables: ✅ (ml_models, ml_feature_data, ml_predictions, ml_backtest_results)"
	@echo "   - Indexes: ✅"
	@echo "   - Reference data: ✅"

# Update comprehensive start command
start: setup-docker init-dev init-test init-prod setup-airflow trigger-dev-dag
	@echo "🎉 Complete infrastructure deployment finished!"
	@echo ""
	@echo "📊 **Available Environments:**"
	@echo "   - dev_stock_data:  Development (ETL + ML) - Active"
	@echo "   - test_stock_data: Testing (ETL + ML) - Active"  
	@echo "   - prod_stock_data: Production (ETL + ML) - Ready"
	@echo ""
	@echo "🚀 **Available DAGs:**"
	@echo "   ETL Pipelines:"
	@echo "   - dev_stock_etl_pipeline:  Development ETL (active)"
	@echo "   - test_stock_etl_pipeline: Test ETL (paused)"
	@echo "   - prod_stock_etl_pipeline: Production ETL (paused)"
	@echo ""
	@echo "   ML Pipelines:"
	@echo "   - dev_ml_pipeline_*:  Development ML per stock (active)"
	@echo "   - test_ml_pipeline_*: Test ML per stock (active)"
	@echo "   - prod_ml_pipeline_*: Production ML per stock (paused)"

# Add ML-specific triggers
trigger-dev-ml-dags:
	@echo "🚀 Triggering all development ML DAGs..."
	# Trigger all dev_ml_pipeline_* DAGs
	
trigger-test-ml-dags:
	@echo "🚀 Triggering all test ML DAGs..."
	# Trigger all test_ml_pipeline_* DAGs
	
trigger-prod-ml-dags:
	@echo "🚀 Triggering all production ML DAGs..."
	# Trigger all prod_ml_pipeline_* DAGs
```

#### **2.2 CLI Database Initialization Enhancement**
Ensure `stock_etl.cli database init-prod` creates `prod_stock_data` schema with ML tables:

```python
# In stock_etl/cli.py (likely already works via Jinja2 template)
@database_group.command()
@click.option('--schema', default='prod_stock_data')
def init_prod(schema: str):
    """Initialize production database schema with ML tables"""
    # Uses sql/schema_template.sql.j2 which already includes ML tables
    # Schema type: "production" 
```

### **Phase 3: Environment-Specific Configuration**

#### **3.1 DAG Naming Convention**
Following ETL pattern:

**ETL DAGs:**
- `dev_stock_etl_pipeline`
- `test_stock_etl_pipeline` 
- `prod_stock_etl_pipeline`

**ML DAGs (per-stock):**
- `dev_ml_pipeline_xtb`
- `dev_ml_pipeline_cdr`
- `test_ml_pipeline_xtb`
- `test_ml_pipeline_cdr`
- `prod_ml_pipeline_xtb`
- `prod_ml_pipeline_cdr`

#### **3.2 Environment-Specific Settings**

| Environment | Schedule | Retries | Grid Search | Web Ready | Paused |
|-------------|----------|---------|-------------|-----------|---------|
| **dev** | Manual | 1 | quick | Yes | No |
| **test** | Manual | 1 | comprehensive | Yes | No |
| **prod** | 6 PM weekdays | 3 | production | Yes | Yes |

#### **3.3 Schema Isolation**
Each environment operates on its own schema:
- **Development**: `dev_stock_data` (sample/mock data)
- **Testing**: `test_stock_data` (real historical data)
- **Production**: `prod_stock_data` (production data)

## 📋 **Implementation TODO List**

### **Phase 1: Multi-Environment ML DAGs**
- [ ] Refactor `stock_etl/airflow_dags/stock_ml_dag.py`

### **Phase 2: Infrastructure Updates** 
- [ ] Update Makefile with `init-prod` ML support
- [ ] Update `make start` to include production initialization
- [ ] Add ML DAG trigger commands to Makefile
- [ ] Verify CLI `init-prod` works with ML tables
- [ ] Test complete infrastructure deployment

### **Phase 3: Production Deployment**
- [ ] Initialize `prod_stock_data` schema with ML tables
- [ ] Generate production ML DAGs (initially paused)
- [ ] Verify schema isolation between environments
- [ ] Test ML DAG execution across all environments
- [ ] Document production deployment procedures

### **Phase 4: Testing & Validation**
- [ ] Test concurrent ML DAG execution across environments
- [ ] Validate CPU optimization works in multi-environment setup
- [ ] Verify database isolation and no cross-schema contamination
- [ ] Test Makefile automation commands
- [ ] Performance testing with production-scale data

## 🎯 **Expected Outcomes**

### **Multi-Environment ML DAGs**
```bash
# After implementation:
docker-compose exec airflow airflow dags list | grep ml_pipeline

# Expected output:
dev_ml_pipeline_bdx          | /opt/airflow/dags/stock_ml_dag_environments.py | ml_pipeline | False
dev_ml_pipeline_cdr          | /opt/airflow/dags/stock_ml_dag_environments.py | ml_pipeline | False  
dev_ml_pipeline_xtb          | /opt/airflow/dags/stock_ml_dag_environments.py | ml_pipeline | False
test_ml_pipeline_bdx         | /opt/airflow/dags/stock_ml_dag_environments.py | ml_pipeline | False
test_ml_pipeline_cdr         | /opt/airflow/dags/stock_ml_dag_environments.py | ml_pipeline | False
test_ml_pipeline_xtb         | /opt/airflow/dags/stock_ml_dag_environments.py | ml_pipeline | False
prod_ml_pipeline_bdx         | /opt/airflow/dags/stock_ml_dag_environments.py | ml_pipeline | True
prod_ml_pipeline_cdr         | /opt/airflow/dags/stock_ml_dag_environments.py | ml_pipeline | True  
prod_ml_pipeline_xtb         | /opt/airflow/dags/stock_ml_dag_environments.py | ml_pipeline | True
```

### **Schema Verification**
```sql
-- Verify all environments have ML tables
-- dev_stock_data
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'dev_stock_data' AND table_name LIKE 'ml_%';

-- test_stock_data  
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'test_stock_data' AND table_name LIKE 'ml_%';

-- prod_stock_data (NEW)
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'prod_stock_data' AND table_name LIKE 'ml_%';

-- Expected: ml_models, ml_feature_data, ml_predictions, ml_backtest_results
```

### **Makefile Automation**
```bash
# Complete deployment with all environments
make start

# Environment-specific ML DAG triggering
make trigger-dev-ml-dags     # All dev_ml_pipeline_* DAGs
make trigger-test-ml-dags    # All test_ml_pipeline_* DAGs  
make trigger-prod-ml-dags    # All prod_ml_pipeline_* DAGs (when ready)
```

## 🔄 **Migration Path**

### **Current → Target State**
1. **Current**: Single `stock_ml_dag.py` hardcoded to `test_stock_data`
2. **Target**: Multi-environment `stock_ml_dag_environments.py` with dynamic schema support

### **Backward Compatibility**
- Keep existing `stock_ml_dag.py` temporarily during transition
- New environment DAGs will be named differently (no conflicts)
- Gradual migration: test → validate → replace

### **Rollback Plan**
- Rename old `stock_ml_dag.py` to `stock_ml_dag_single.py` (backup)
- If issues arise, can quickly revert to single-environment approach
- Database schemas remain unchanged (no data loss risk)

## ⚡ **Performance Considerations**

### **CPU Optimization Maintained**
- 2-core limit per DAG applies to all environments
- Concurrent execution improves: 10+ ML DAGs across environments
- Resource isolation: dev/test/prod don't compete for same DAG slots

### **Database Performance**
- Schema isolation prevents query conflicts
- Each environment has dedicated indexes
- Production gets dedicated database resources

### **Scaling Benefits**
- Development work doesn't impact production
- Independent testing without affecting other environments  
- Production can run scheduled while dev/test run on-demand

## 🎉 **Success Criteria**

### **Technical Success**
- [ ] All 3 environments (dev/test/prod) have ML DAG support
- [ ] Dynamic schema configuration works correctly
- [ ] CPU optimization (2 cores) maintained across environments
- [ ] No hardcoded schema references remain
- [ ] Complete infrastructure deployment via `make start`

### **Operational Success**
- [ ] Development ML training works in `dev_stock_data`
- [ ] Testing ML training works in `test_stock_data`  
- [ ] Production ML training ready in `prod_stock_data` (paused)
- [ ] Schema isolation verified (no cross-contamination)
- [ ] Makefile automation for all environments

### **Production Readiness**
- [ ] Production ML DAGs generated but paused
- [ ] Production schedule configured (6 PM weekdays)
- [ ] Enhanced retry logic (3 retries vs 1)
- [ ] Production grid search optimization
- [ ] Monitoring and alerting ready

---

## 📝 **Next Steps**

1. **Implement Phase 1**: Create multi-environment ML DAG file
2. **Update Makefile**: Add production ML support
3. **Test Infrastructure**: Verify complete deployment works
4. **Validate Environments**: Test ML DAG execution across dev/test/prod
5. **Document Results**: Update README.md with new multi-environment capabilities

**Estimated Implementation Time**: 2-3 hours
**Risk Level**: Low (follows proven ETL pattern)
**Dependencies**: Schema template already supports ML tables ✅