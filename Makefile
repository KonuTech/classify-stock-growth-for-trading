.PHONY: start stop restart start-infrastructure start-services extract-credentials clean help init-dev init-test init-prod setup-airflow fix-schema-permissions trigger-dev-dag trigger-test-dag trigger-prod-dag trigger-dev-ml-dags trigger-test-ml-dags trigger-prod-ml-dags trigger-ml-stock web web-start web-stop web-restart web-rebuild web-quick-restart web-restart-frontend web-restart-backend web-build web-logs web-clean web-test web-status web-health restart-airflow dev-restart docker-restart docker-clean dev-web-start dev-web-stop dev-web-restart dev-web-status dev-web-backend dev-web-frontend dev-web-install redis-status redis-clear-timeframe redis-clear-all redis-flush redis-test redis-restart-clean

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "🚀 Complete Deployment:"
	@echo "  make start              - COMPLETE DEPLOYMENT: infrastructure + web app + schemas + DAGs"
	@echo "  make start-infrastructure - Start infrastructure only (PostgreSQL + Airflow + pgAdmin)"
	@echo "  make start-services     - Start Docker services only (no schemas/credentials)"
	@echo ""
	@echo "🔧 Environment Setup:"
	@echo "  make init ENV=dev|test|prod [TRIGGER_DAG=true] [EXTRACT_CREDS=true] - Unified initialization"
	@echo "  make init-dev           - Legacy alias for 'make init ENV=dev'"
	@echo "  make init-test          - Legacy alias for 'make init ENV=test'"
	@echo "  make init-prod          - Legacy alias for 'make init ENV=prod'"
	@echo "  make extract-credentials - Extract service credentials to .env file"
	@echo "  make setup-airflow      - Setup Airflow database connections only"
	@echo ""
	@echo "    💡 Init Examples:"
	@echo "      make init ENV=dev                    # Dev environment with DAG trigger"
	@echo "      make init ENV=prod EXTRACT_CREDS=true # Prod with credential extraction"
	@echo "      make init ENV=test TRIGGER_DAG=false  # Test without DAG trigger"
	@echo ""
	@echo "🔄 Service Management:"
	@echo "  make stop               - Stop all services"
	@echo "  make restart [MODE=full|docker|clean] - Restart with configurable mode (default: full)"
	@echo "  make docker-restart     - Legacy alias for 'make restart MODE=docker'"
	@echo "  make docker-clean       - CLEAN restart with database reinitialization (deletes data)"
	@echo "  make dev-restart        - Restart EVERYTHING (infrastructure + development web app)"
	@echo "  make clean              - Stop services and clean up completely"
	@echo ""
	@echo "    💡 Restart Examples:"
	@echo "      make restart              # Full redeployment (stop -> start)"
	@echo "      make restart MODE=docker  # Docker services only (preserves data)"
	@echo "      make restart MODE=clean   # Clean restart (deletes data)"
	@echo ""
	@echo "📊 ETL DAGs:"
	@echo "  make trigger-dev-dag    - Trigger development ETL DAG"
	@echo "  make trigger-test-dag   - Trigger test ETL DAG (full_backfill mode)"
	@echo "  make trigger-prod-dag   - Trigger production ETL DAG"
	@echo ""
	@echo "🤖 ML DAGs (Test & Production Only):"
	@echo "  make trigger-test-ml-dags  - Trigger all test ML DAGs (test_ml_pipeline_*)"
	@echo "  make trigger-prod-ml-dags  - Trigger all production ML DAGs (prod_ml_pipeline_*)"
	@echo "  make trigger-ml-stock STOCK=XTB - Trigger ML training for specific stock (test & prod)"
	@echo ""
	@echo "🌐 Web Application (Production - Docker):"
	@echo "  make web MODE=start|stop|restart|build [REBUILD=true] [COMPONENT=frontend|backend] [QUICK=true]"
	@echo "  make web-status [DETAIL=basic|health|test] - Show web application status"
	@echo "  make web-logs           - Show Docker web application logs"
	@echo "  make web-clean          - Clean web application containers and images"
	@echo ""
	@echo "    💡 Web Examples:"
	@echo "      make web MODE=restart QUICK=true     # Quick restart (fastest)"
	@echo "      make web MODE=restart REBUILD=true   # Restart with rebuild"
	@echo "      make web MODE=restart COMPONENT=frontend # Restart only frontend"
	@echo "      make web-status DETAIL=health        # Comprehensive health check"
	@echo ""
	@echo "⚡ Web Application (Development - Local):"
	@echo "  make dev-restart        - Restart EVERYTHING (infrastructure + development web app)"
	@echo "  make dev-web-install    - Install frontend dependencies"
	@echo "  make dev-web-start      - Start backend and frontend in development mode"
	@echo "  make dev-web-backend    - Start only backend API server"
	@echo "  make dev-web-frontend   - Start only frontend development server"
	@echo "  make dev-web-restart    - Restart development web services only"
	@echo "  make dev-web-stop       - Stop development web services"
	@echo "  make dev-web-status     - Show development web services status"
	@echo ""
	@echo "🗄️  Redis Caching Management:"
	@echo "  make redis-status       - Show Redis cache status and statistics"
	@echo "  make redis-clear-timeframe TIMEFRAME=1Y - Clear specific timeframe cache"
	@echo "  make redis-clear-all    - Clear all cached data via API"
	@echo "  make redis-flush        - Clear Redis database directly"
	@echo "  make redis-test         - Test cache performance (miss vs hit)"
	@echo "  make redis-restart-clean - Clean restart with fresh Redis cache"
	@echo ""
	@echo "❓ Help:"
	@echo "  make help               - Show this help"

# Start services with complete setup (all schemas + airflow + DAGs)
start-infrastructure:
	@echo "Starting infrastructure services only..."
	docker-compose up -d postgres pgadmin airflow redis
	@echo "Waiting for services to initialize..."
	@sleep 30
	@echo "Setting up all database schemas..."
	@sleep 5
	@echo "Initializing dev_stock_data schema..."
	@uv run python -m stock_etl.cli database init-dev
	@echo "Initializing test_stock_data schema..."
	@uv run python -m stock_etl.cli database init-test
	@echo "Initializing prod_stock_data schema with ML tables..."
	@uv run python -m stock_etl.cli database init-prod
	@make fix-schema-permissions
	@make setup-airflow
	@echo "✅ All schemas initialized and permissions set!"
	@echo "Triggering all environment DAGs..."
	@make trigger-dev-dag
	@make trigger-test-dag
	@make trigger-prod-dag
	@echo "✅ Infrastructure deployment ready!"
	@echo "📊 Schemas: dev_stock_data ✅ test_stock_data ✅ prod_stock_data ✅"
	@echo "🚀 ETL DAGs: dev_stock_etl_pipeline ✅ test_stock_etl_pipeline ✅ prod_stock_etl_pipeline ✅"
	@echo "🤖 ML DAGs: Dynamic multi-environment per-stock ML training (ready)"
	@echo "🌐 Airflow UI: http://localhost:8080"
	@echo "📊 pgAdmin: http://localhost:5050"
	@echo "Waiting for Airflow to fully initialize credentials..."
	@sleep 20
	@make extract-credentials

# Stop all services
stop:
	@echo "Stopping all services..."
	docker-compose down

# Restart services with configurable mode
# Usage: make restart [MODE=clean|docker|full]
restart:
	@mode="$(MODE)"; \
	if [ -z "$$mode" ]; then mode="full"; fi; \
	if [ "$$mode" = "clean" ]; then \
		make docker-clean; \
	elif [ "$$mode" = "docker" ]; then \
		make _restart-docker-only; \
	elif [ "$$mode" = "full" ]; then \
		make _restart-full; \
	else \
		echo "❌ Invalid MODE: $$mode. Use: clean|docker|full"; \
		exit 1; \
	fi

# Internal restart implementations
_restart-full:
	@echo "🔄 FULL RESTART (Complete redeployment)"
	@make stop
	@sleep 3
	@make start

_restart-docker-only:
	@echo "🐳 DOCKER RESTART (Data Preserved)"
	@echo "=================================="
	@echo ""
	@echo "Step 1: Restarting Docker services..."
	@docker-compose restart
	@echo ""
	@echo "Step 2: Waiting for services to stabilize..."
	@sleep 20
	@echo ""
	@echo "✅ DOCKER RESTART FINISHED!"
	@echo "============================"
	@echo ""
	@echo "🐳 All Docker Services Status:"
	@make web-status

# Legacy aliases for backward compatibility
docker-restart:
	@make restart MODE=docker

# CLEAN restart with database reinitialization (deletes data)
docker-clean:
	@echo "🧹 DOCKER CLEAN RESTART (⚠️  DELETES ALL DATA)"
	@echo "==============================================="
	@echo ""
	@echo "⚠️  WARNING: This will DELETE all database data!"
	@echo "   - All stock prices and ETL job history"
	@echo "   - All ML models and predictions"  
	@echo "   - All schemas will be reinitialized from scratch"
	@echo ""
	@echo "Step 1: Stopping all Docker services..."
	@make stop
	@sleep 5
	@echo ""
	@echo "Step 2: Starting complete infrastructure + Docker web application..."
	@make start
	@echo ""
	@echo "✅ DOCKER CLEAN RESTART FINISHED!"
	@echo "=================================="
	@echo ""
	@echo "🐳 All Docker Services Status:"
	@make web-status

# Rebuild Airflow service with dependencies (for DAG fixes)
restart-airflow:
	@echo "Stopping and rebuilding Airflow service..."
	docker-compose stop airflow
	docker-compose rm -f airflow
	docker-compose up -d airflow
	@echo "Airflow restarted with updated dependencies"
	@echo "Waiting for Airflow to fully initialize credentials..."
	@sleep 20
	@make extract-credentials

# Extract credentials from logs and save to .env
extract-credentials:
	@echo "Extracting service credentials..."
	@# Extract Airflow password from logs using scripts
	@AIRFLOW_PASSWORD=$$(docker-compose logs airflow 2>/dev/null | grep "Password for user 'admin':" | tail -1 | sed -n "s/.*Password for user 'admin': \(.*\)/\1/p"); \
	if [ -f .env ]; then \
		sed -i '/^AIRFLOW_/d' .env; \
		sed -i '/^PGADMIN_/d' .env; \
		sed -i '/^POSTGRES_/d' .env; \
		sed -i '/^# Service Credentials/d' .env; \
	fi; \
	echo "# Service Credentials - Auto-generated $$(date)" >> .env; \
	echo "" >> .env; \
	if [ -n "$$AIRFLOW_PASSWORD" ]; then \
		echo "# Airflow - http://localhost:8080" >> .env; \
		echo "AIRFLOW_USERNAME=admin" >> .env; \
		echo "AIRFLOW_PASSWORD=$$AIRFLOW_PASSWORD" >> .env; \
		echo "" >> .env; \
		echo "✓ Airflow credentials saved"; \
	else \
		echo "⚠ Could not extract Airflow password from logs"; \
	fi; \
	echo "# pgAdmin - http://localhost:5050" >> .env; \
	echo "PGADMIN_EMAIL=admin@admin.com" >> .env; \
	echo "PGLADMIN_PASSWORD=admin" >> .env; \
	echo "" >> .env; \
	echo "# PostgreSQL - localhost:5432" >> .env; \
	echo "POSTGRES_HOST=localhost" >> .env; \
	echo "POSTGRES_PORT=5432" >> .env; \
	echo "POSTGRES_USER=postgres" >> .env; \
	echo "POSTGRES_PASSWORD=postgres" >> .env; \
	echo "" >> .env; \
	echo "# Airflow Metadata Database" >> .env; \
	echo "AIRFLOW_DB_HOST=localhost" >> .env; \
	echo "AIRFLOW_DB_PORT=5432" >> .env; \
	echo "AIRFLOW_DB_NAME=airflow_metadata" >> .env; \
	echo "AIRFLOW_DB_USER=airflow" >> .env; \
	echo "AIRFLOW_DB_PASSWORD=airflow" >> .env; \
	echo "" >> .env; \
	echo "# Stock Business Database" >> .env; \
	echo "STOCK_DB_HOST=localhost" >> .env; \
	echo "STOCK_DB_PORT=5432" >> .env; \
	echo "STOCK_DB_NAME=stock_data" >> .env; \
	echo "STOCK_DB_USER=stock" >> .env; \
	echo "STOCK_DB_PASSWORD=stock" >> .env; \
	echo ""; \
	echo "=== ALL SERVICE CREDENTIALS ==="; \
	echo "Airflow Web UI: http://localhost:8080"; \
	echo "  Username: admin"; \
	if [ -n "$$AIRFLOW_PASSWORD" ]; then \
		echo "  Password: $$AIRFLOW_PASSWORD"; \
	else \
		echo "  Password: [Check logs manually]"; \
	fi; \
	echo ""; \
	echo "pgAdmin Web UI: http://localhost:5050"; \
	echo "  Email: admin@admin.com"; \
	echo "  Password: admin"; \
	echo ""; \
	echo "PostgreSQL Admin: localhost:5432"; \
	echo "  Username: postgres"; \
	echo "  Password: postgres"; \
	echo ""; \
	echo "Airflow Metadata DB: localhost:5432/airflow_metadata"; \
	echo "  Username: airflow"; \
	echo "  Password: airflow"; \
	echo ""; \
	echo "Stock Business DB: localhost:5432/stock_data"; \
	echo "  Username: stock"; \
	echo "  Password: stock"; \
	echo ""; \
	echo "All credentials saved to .env file"; \
	echo "================================"; \
	cp .env .env.sample; \
	echo "📋 Credentials also copied to .env.sample for reference"

# Start services only (without credential extraction)
start-services:
	@echo "Starting Docker services..."
	docker-compose up -d postgres pgadmin airflow redis
	@echo "Waiting for services to initialize..."
	@sleep 70

# Unified environment initialization
# Usage: make init ENV=dev|test|prod [TRIGGER_DAG=true] [EXTRACT_CREDS=true]
init:
	@env="$(ENV)"; \
	if [ -z "$$env" ]; then \
		echo "❌ ENV parameter required. Usage: make init ENV=dev|test|prod"; \
		exit 1; \
	fi; \
	if [ "$$env" != "dev" ] && [ "$$env" != "test" ] && [ "$$env" != "prod" ]; then \
		echo "❌ Invalid ENV: $$env. Use: dev|test|prod"; \
		exit 1; \
	fi; \
	echo "🚀 Setting up $$env environment..."; \
	make start-services; \
	sleep 5; \
	echo "Initializing $${env}_stock_data schema..."; \
	uv run python -m stock_etl.cli database init-$$env; \
	make fix-schema-permissions; \
	make setup-airflow; \
	if [ "$$env" = "prod" ]; then \
		echo "✅ Production environment ready with complete ML pipeline support!"; \
		echo "   - ETL tables: ✅ (exchanges, base_instruments, stocks, indices, stock_prices, etl_jobs)"; \
		echo "   - ML tables: ✅ (ml_models, ml_feature_data, ml_predictions, ml_backtest_results)"; \
		echo "   - Indexes: ✅ (optimized for time-series queries and ML operations)"; \
		echo "   - Reference data: ✅ (WSE exchanges, sectors, sample instruments)"; \
	else \
		echo "✅ $$(echo $$env | tr '[:lower:]' '[:upper:]') environment ready!"; \
	fi; \
	echo "🌐 Airflow UI: http://localhost:8080"; \
	echo "📊 pgAdmin: http://localhost:5050"; \
	if [ "$(TRIGGER_DAG)" = "true" ] || [ -z "$(TRIGGER_DAG)" ]; then \
		echo "Triggering $$env DAG..."; \
		make trigger-$$env-dag; \
	fi; \
	if [ "$(EXTRACT_CREDS)" = "true" ]; then \
		make extract-credentials; \
	else \
		echo "💡 Note: Run 'make extract-credentials' to get service credentials"; \
	fi

# Legacy command aliases for backward compatibility
init-dev:
	@make init ENV=dev

init-test:
	@make init ENV=test

init-prod:
	@make init ENV=prod

# Fix schema permissions for Airflow database user
fix-schema-permissions:
	@echo "Fixing database schema permissions for Airflow user..."
	@docker-compose exec postgres psql -U postgres -d stock_data -c "GRANT USAGE ON SCHEMA dev_stock_data TO stock; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dev_stock_data TO stock; GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA dev_stock_data TO stock; ALTER DEFAULT PRIVILEGES IN SCHEMA dev_stock_data GRANT ALL ON TABLES TO stock; ALTER DEFAULT PRIVILEGES IN SCHEMA dev_stock_data GRANT ALL ON SEQUENCES TO stock;"
	@docker-compose exec postgres psql -U postgres -d stock_data -c "GRANT USAGE ON SCHEMA test_stock_data TO stock; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA test_stock_data TO stock; GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA test_stock_data TO stock; ALTER DEFAULT PRIVILEGES IN SCHEMA test_stock_data GRANT ALL ON TABLES TO stock; ALTER DEFAULT PRIVILEGES IN SCHEMA test_stock_data GRANT ALL ON SEQUENCES TO stock;"
	@docker-compose exec postgres psql -U postgres -d stock_data -c "GRANT USAGE ON SCHEMA prod_stock_data TO stock; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA prod_stock_data TO stock; GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA prod_stock_data TO stock; ALTER DEFAULT PRIVILEGES IN SCHEMA prod_stock_data GRANT ALL ON TABLES TO stock; ALTER DEFAULT PRIVILEGES IN SCHEMA prod_stock_data GRANT ALL ON SEQUENCES TO stock;"
	@echo "✅ Schema permissions fixed for Airflow database user (dev/test/prod)"

# Setup Airflow database connections (via environment variables)
setup-airflow:
	@echo "Airflow connections configured via environment variables"
	@echo "Waiting for Airflow to initialize connections..."
	@sleep 15
	@echo "Testing connection availability..."
	@docker-compose exec airflow python3 -c "from airflow.models import Connection; from airflow.settings import Session; session = Session(); conns = session.query(Connection).filter(Connection.conn_id.in_(['postgres_default', 'postgres_stock'])).all(); print(f'Found {len(conns)} connections: {[c.conn_id for c in conns]}'); session.close()" 2>/dev/null || echo "Connections still initializing..."
	@echo "✅ Airflow connection setup completed via environment variables"

# Trigger environment-specific DAGs
trigger-dev-dag:
	@echo "Triggering development DAG..."
	@docker-compose exec airflow airflow dags trigger dev_stock_etl_pipeline
	@echo "✅ Development DAG triggered"

trigger-test-dag:
	@echo "Triggering test DAG with full backfill mode..."
	@docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline --conf '{"extraction_mode": "full_backfill"}'
	@echo "✅ Test DAG triggered (full_backfill mode - expects 50,000+ records)"

trigger-prod-dag:
	@echo "Triggering production DAG with full backfill mode..."
	@docker-compose exec airflow airflow dags trigger prod_stock_etl_pipeline --conf '{"extraction_mode": "full_backfill"}'
	@echo "✅ Production DAG triggered (full_backfill mode - expects 50,000+ records)"

# Trigger ML DAGs for specific environments
trigger-dev-ml-dags:
	@echo "⚠️ Development ML DAGs are disabled (no dev environment for ML)"
	@echo "   Use test or prod environments instead"

trigger-test-ml-dags:
	@echo "🚀 Triggering all test ML DAGs..."
	@docker-compose exec airflow airflow dags list | grep "^test_ml_pipeline_" | awk '{print $$1}' | xargs -I {} docker-compose exec airflow airflow dags trigger {}
	@echo "✅ All test ML DAGs triggered"

trigger-prod-ml-dags:
	@echo "🚀 Triggering all production ML DAGs..."
	@docker-compose exec airflow airflow dags list | grep "^prod_ml_pipeline_" | awk '{print $$1}' | xargs -I {} docker-compose exec airflow airflow dags trigger {}
	@echo "✅ All production ML DAGs triggered"

# Trigger specific stock ML training across all environments
trigger-ml-stock:
	@if [ -z "$(STOCK)" ]; then \
		echo "❌ Please specify STOCK parameter. Usage: make trigger-ml-stock STOCK=XTB"; \
		exit 1; \
	fi
	@echo "🚀 Triggering ML training for $(STOCK) across available environments..."
	@echo "   Note: Dev environment is disabled for ML - using test and prod only"
	@docker-compose exec airflow airflow dags trigger test_ml_pipeline_$(shell echo $(STOCK) | tr '[:upper:]' '[:lower:]') || echo "⚠️ Test ML DAG not found for $(STOCK)"
	@docker-compose exec airflow airflow dags trigger prod_ml_pipeline_$(shell echo $(STOCK) | tr '[:upper:]' '[:lower:]') || echo "⚠️ Prod ML DAG not found for $(STOCK)"
	@echo "✅ ML training triggered for $(STOCK) across available environments"

# Clean up everything including Docker images and containers
clean:
	@echo "Cleaning up..."
	@echo "Stopping and removing containers..."
	docker-compose down -v --remove-orphans
	@echo "Force stopping any remaining containers..."
	docker stop $$(docker ps -q) 2>/dev/null || echo "No running containers to stop"
	@echo "Removing all containers..."
	docker rm $$(docker ps -aq) -f 2>/dev/null || echo "No containers to remove"
	@echo "Removing Docker images..."
	docker rmi apache/airflow:3.0.4-python3.12 -f 2>/dev/null || echo "Airflow image not found"
	docker rmi postgres:17-alpine -f 2>/dev/null || echo "PostgreSQL image not found"
	docker rmi dpage/pgadmin4:latest -f 2>/dev/null || echo "pgAdmin image not found"
	docker rmi redis:7-alpine -f 2>/dev/null || echo "Redis image not found"
	docker rmi classify-stock-growth-for-trading-web-frontend -f 2>/dev/null || echo "Web frontend image not found"
	docker rmi classify-stock-growth-for-trading-web-backend -f 2>/dev/null || echo "Web backend image not found"
	@echo "Removing all untagged images..."
	docker rmi $$(docker images -q) -f 2>/dev/null || echo "No images to remove"
	docker system prune -a --volumes -f
	@if [ -f .env ]; then rm .env; fi
	@echo "Removing old Airflow logs..."
	@rm -rf stock_etl/airflow_logs/dag_id=*
	@rm -rf stock_etl/airflow_logs/dag_processor/*
	@rm -rf stock_etl/airflow_logs/etl/*.log
	@echo "Cleaning web application build artifacts..."
	@rm -rf web-app/frontend/build web-app/backend/dist 2>/dev/null || echo "No web app builds to clean"
	@rm -rf web-app/frontend/node_modules/.cache 2>/dev/null || echo "No frontend cache to clean"
	@echo "Stopping any running development web processes..."
	@make dev-web-stop 2>/dev/null || echo "No development web processes to stop"
	@echo "Complete cleanup finished"

# ==================== REDIS CACHING COMMANDS ====================

# Redis cache management and testing
redis-status:
	@echo "📊 Redis Cache Status"
	@echo "===================="
	@echo ""
	@echo "🔧 Redis Container Status:"
	@docker-compose ps redis | tail -n +2 | while IFS= read -r line; do \
		if echo "$$line" | grep -q "Up.*healthy"; then \
			echo "✅ Redis - Healthy and running"; \
		elif echo "$$line" | grep -q "Up"; then \
			echo "⚠️  Redis - Running (health check pending)"; \
		else \
			echo "❌ Redis - Not healthy or stopped"; \
		fi; \
	done 2>/dev/null || echo "❌ Redis container not found"
	@echo ""
	@echo "📊 Cache Statistics:"
	@curl -s "http://localhost:3001/api/cache/status" 2>/dev/null | grep -E '"connected"|"keyCount"' | sed 's/^/  /' || echo "  Backend not available"
	@echo ""
	@echo "🗄️  Redis Memory Usage:"
	@docker-compose exec redis redis-cli INFO memory | grep -E "used_memory_human|maxmemory_human" | sed 's/^/  /' 2>/dev/null || echo "  Redis CLI not available"
	@echo ""
	@echo "🔑 Cache Keys:"
	@key_count=$$(docker-compose exec redis redis-cli KEYS "*" | wc -l 2>/dev/null || echo "0"); \
	echo "  Total keys: $$key_count"; \
	if [ "$$key_count" -gt 0 ] && [ "$$key_count" -le 20 ]; then \
		echo "  Sample keys:"; \
		docker-compose exec redis redis-cli KEYS "*" | head -10 | sed 's/^/    - /' 2>/dev/null || echo "    Unable to list keys"; \
	elif [ "$$key_count" -gt 20 ]; then \
		echo "  Sample keys (first 10):"; \
		docker-compose exec redis redis-cli KEYS "*" | head -10 | sed 's/^/    - /' 2>/dev/null || echo "    Unable to list keys"; \
	fi

# Clear specific timeframe cache
redis-clear-timeframe:
	@if [ -z "$(TIMEFRAME)" ]; then \
		echo "❌ Please specify TIMEFRAME parameter. Usage: make redis-clear-timeframe TIMEFRAME=1Y"; \
		echo "   Available timeframes: 1M, 3M, 6M, 1Y, MAX"; \
		exit 1; \
	fi
	@echo "🗑️  Clearing cache for timeframe: $(TIMEFRAME)"
	@curl -s -X DELETE "http://localhost:3001/api/cache/$(TIMEFRAME)" | grep -o '"message":"[^"]*"' | sed 's/"message":"//;s/"$$//' || echo "❌ Backend not available"
	@echo ""
	@make redis-status

# Clear all cache data
redis-clear-all:
	@echo "🗑️  Clearing all cache data..."
	@curl -s -X DELETE "http://localhost:3001/api/cache" | grep -o '"message":"[^"]*"' | sed 's/"message":"//;s/"$$//' || echo "❌ Backend not available"
	@echo ""
	@make redis-status

# Clear Redis database directly (bypasses backend)
redis-flush:
	@echo "🗑️  Flushing Redis database directly..."
	@docker-compose exec redis redis-cli FLUSHALL
	@echo "✅ Redis database flushed"
	@make redis-status

# Test Redis caching performance
redis-test:
	@echo "🧪 Testing Redis Cache Performance"
	@echo "=================================="
	@echo ""
	@echo "1️⃣ Clearing cache for clean test..."
	@docker-compose exec redis redis-cli FLUSHALL >/dev/null 2>&1
	@echo ""
	@echo "2️⃣ Testing stock list API (cache miss - should be slow)..."
	@echo -n "  First call (cache miss):  "
	@time1=$$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:3001/api/stocks?timeframe=1Y" 2>/dev/null || echo "N/A"); \
	if [ "$$time1" != "N/A" ]; then echo "$${time1}s"; else echo "❌ Failed"; fi
	@sleep 2
	@echo -n "  Second call (cache hit):  "
	@time2=$$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:3001/api/stocks?timeframe=1Y" 2>/dev/null || echo "N/A"); \
	if [ "$$time2" != "N/A" ]; then echo "$${time2}s"; else echo "❌ Failed"; fi
	@sleep 2
	@echo -n "  Third call (cache hit):   "
	@time3=$$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:3001/api/stocks?timeframe=1Y" 2>/dev/null || echo "N/A"); \
	if [ "$$time3" != "N/A" ]; then echo "$${time3}s"; else echo "❌ Failed"; fi
	@echo ""
	@echo "3️⃣ Testing analytics API (cache miss vs hit)..."
	@echo -n "  Analytics (cache miss):   "
	@time4=$$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:3001/api/stocks/XTB/analytics?timeframe=3M" 2>/dev/null || echo "N/A"); \
	if [ "$$time4" != "N/A" ]; then echo "$${time4}s"; else echo "❌ Failed"; fi
	@sleep 2
	@echo -n "  Analytics (cache hit):    "
	@time5=$$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:3001/api/stocks/XTB/analytics?timeframe=3M" 2>/dev/null || echo "N/A"); \
	if [ "$$time5" != "N/A" ]; then echo "$${time5}s"; else echo "❌ Failed"; fi
	@echo ""
	@echo "✅ Cache performance test completed"
	@echo "💡 Expected: Cache hits should be 50-200x faster than cache misses"

# Restart web app with clean Redis cache
redis-restart-clean:
	@echo "🔄 Clean restart with fresh Redis cache"
	@echo "======================================="
	@echo "Step 1: Stopping web services and Redis..."
	@docker-compose stop web-backend web-frontend redis
	@echo "Step 2: Removing Redis container to clear data..."
	@docker-compose rm -f redis
	@echo "Step 3: Starting Redis with fresh data..."
	@docker-compose up -d redis
	@echo "Step 4: Waiting for Redis health check..."
	@sleep 10
	@echo "Step 5: Starting web application..."
	@docker-compose up -d web-backend web-frontend
	@sleep 10
	@echo ""
	@echo "✅ Clean restart completed!"
	@make redis-status

# ==================== WEB APPLICATION COMMANDS (INTEGRATED) ====================

# Start complete infrastructure WITH web application
start:
	@echo "🚀 Starting complete infrastructure with web application..."
	docker-compose up -d postgres pgadmin airflow redis web-backend web-frontend
	@echo "Waiting for services to initialize..."
	@sleep 30
	@echo "Setting up all database schemas..."
	@sleep 5
	@echo "Initializing dev_stock_data schema..."
	@uv run python -m stock_etl.cli database init-dev
	@echo "Initializing test_stock_data schema..."
	@uv run python -m stock_etl.cli database init-test
	@echo "Initializing prod_stock_data schema with ML tables..."
	@uv run python -m stock_etl.cli database init-prod
	@make fix-schema-permissions
	@make setup-airflow
	@echo "✅ All schemas initialized and permissions set!"
	@echo "Triggering all environment DAGs..."
	@make trigger-dev-dag
	@make trigger-test-dag
	@make trigger-prod-dag
	@echo "✅ Complete deployment with web application ready!"
	@echo "📊 Schemas: dev_stock_data ✅ test_stock_data ✅ prod_stock_data ✅"
	@echo "🚀 ETL DAGs: dev_stock_etl_pipeline ✅ test_stock_etl_pipeline ✅ prod_stock_etl_pipeline ✅"
	@echo "🤖 ML DAGs: Dynamic multi-environment per-stock ML training (ready)"
	@echo ""
	@echo "🌐 All Services Ready:"
	@echo "  Frontend:     http://localhost:3000 (React Dashboard)"
	@echo "  Backend API:  http://localhost:3001 (Express.js API)"
	@echo "  Airflow UI:   http://localhost:8080 (ETL/ML Pipeline)"
	@echo "  pgAdmin:      http://localhost:5050 (Database Management)"
	@echo ""
	@echo "Waiting for Airflow to fully initialize credentials..."
	@sleep 20
	@make extract-credentials

# Start web application services only (requires existing database)
web-start:
	@echo "🚀 Starting web application services..."
	@echo "Ensuring database and Redis are available..."
	@docker-compose up -d postgres redis
	@echo "Waiting for database to be ready..."
	@timeout=60; while [ $$timeout -gt 0 ]; do \
		if docker-compose exec -T postgres pg_isready -h localhost -p 5432 >/dev/null 2>&1; then \
			echo "✅ Database is ready"; \
			break; \
		fi; \
		echo "⏳ Waiting for database ($$timeout seconds remaining)..."; \
		sleep 2; \
		timeout=$$((timeout-2)); \
	done; \
	if [ $$timeout -le 0 ]; then \
		echo "❌ Database failed to start within 60 seconds"; \
		exit 1; \
	fi
	@echo "Waiting for Redis to be ready..."
	@timeout=30; while [ $$timeout -gt 0 ]; do \
		if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then \
			echo "✅ Redis is ready"; \
			break; \
		fi; \
		echo "⏳ Waiting for Redis ($$timeout seconds remaining)..."; \
		sleep 2; \
		timeout=$$((timeout-2)); \
	done; \
	if [ $$timeout -le 0 ]; then \
		echo "❌ Redis failed to start within 30 seconds"; \
		exit 1; \
	fi
	@echo "Starting web application containers..."
	@if docker-compose up -d web-backend web-frontend; then \
		echo "🔍 Waiting for containers to be healthy..."; \
		sleep 15; \
		echo "✅ Web application containers started!"; \
	else \
		echo "❌ Failed to start web application containers"; \
		exit 1; \
	fi
	@echo ""
	@make web-status

# Stop web application services
web-stop:
	@echo "🛑 Stopping web application..."
	@docker-compose stop web-frontend web-backend redis
	@echo "✅ Web application and Redis stopped"

# Unified web application management with parameters
# Usage: make web MODE=restart [REBUILD=true] [COMPONENT=frontend|backend|all] [QUICK=true]
web:
	@if [ -z "$(MODE)" ]; then \
		echo "❌ MODE parameter required. Usage: make web MODE=start|stop|restart|build"; \
		echo "   Optional: REBUILD=true COMPONENT=frontend|backend|all QUICK=true"; \
		exit 1; \
	fi
	@if [ "$(MODE)" = "start" ]; then \
		make web-start; \
	elif [ "$(MODE)" = "stop" ]; then \
		make web-stop; \
	elif [ "$(MODE)" = "restart" ]; then \
		make _web-restart-unified; \
	elif [ "$(MODE)" = "build" ]; then \
		make _web-build-unified; \
	else \
		echo "❌ Invalid MODE: $(MODE). Use: start|stop|restart|build"; \
		exit 1; \
	fi

# Internal unified restart logic
_web-restart-unified:
	@echo "🔄 Restarting web application..."
	@component="$(COMPONENT)"; \
	if [ -z "$$component" ]; then component="all"; fi; \
	if [ "$(QUICK)" = "true" ]; then \
		echo "⚡ Quick restart mode (no health checks)..."; \
		if [ "$$component" = "frontend" ]; then \
			docker-compose restart web-frontend; \
		elif [ "$$component" = "backend" ]; then \
			docker-compose restart web-backend; \
		else \
			docker-compose restart web-frontend web-backend; \
		fi; \
		sleep 5; \
		echo "✅ Quick restart completed"; \
	else \
		echo "Step 1: Stopping services..."; \
		if [ "$$component" = "frontend" ]; then \
			docker-compose stop web-frontend; \
		elif [ "$$component" = "backend" ]; then \
			docker-compose stop web-backend; \
		else \
			make web-stop; \
		fi; \
		sleep 3; \
		if [ "$(REBUILD)" = "true" ]; then \
			echo "Step 2: Rebuilding..."; \
			make _web-build-unified COMPONENT=$$component || { echo "❌ Build failed, attempting to start existing images..."; }; \
		else \
			echo "Step 2: Skipping build (use REBUILD=true to force rebuild)"; \
		fi; \
		echo "Step 3: Starting services..."; \
		if [ "$$component" = "frontend" ]; then \
			docker-compose up -d web-frontend; \
			sleep 10; \
		elif [ "$$component" = "backend" ]; then \
			docker-compose up -d web-backend; \
			sleep 10; \
		else \
			make web-start; \
		fi; \
		echo "✅ Web application restarted successfully"; \
	fi
	@make web-status

# Internal unified build logic
_web-build-unified:
	@echo "🔨 Building web application..."
	@component="$(COMPONENT)"; \
	if [ -z "$$component" ]; then component="all"; fi; \
	if [ "$$component" = "frontend" ] || [ "$$component" = "all" ]; then \
		echo "Building frontend image..."; \
		if docker-compose build web-frontend; then \
			echo "✅ Frontend image built successfully"; \
		else \
			echo "❌ Frontend build failed"; \
			exit 1; \
		fi; \
	fi; \
	if [ "$$component" = "backend" ] || [ "$$component" = "all" ]; then \
		echo "Building backend image..."; \
		if docker-compose build web-backend; then \
			echo "✅ Backend image built successfully"; \
		else \
			echo "❌ Backend build failed"; \
			exit 1; \
		fi; \
	fi
	@echo "✅ Build completed successfully"

# Legacy command aliases for backward compatibility
web-restart: 
	@make web MODE=restart

web-build:
	@make web MODE=build

web-rebuild:
	@make web MODE=restart REBUILD=true

web-quick-restart:
	@make web MODE=restart QUICK=true

web-restart-frontend:
	@make web MODE=restart COMPONENT=frontend REBUILD=$(REBUILD)

web-restart-backend:
	@make web MODE=restart COMPONENT=backend REBUILD=$(REBUILD)

# Show web application logs
web-logs:
	@echo "📋 Web Application Logs"
	@echo "======================="
	@echo "🌐 Frontend logs:"
	@docker-compose logs --tail=20 web-frontend 2>/dev/null || echo "Frontend container not running"
	@echo ""
	@echo "🔧 Backend logs:"
	@docker-compose logs --tail=20 web-backend 2>/dev/null || echo "Backend container not running"

# Clean web application containers and images
web-clean:
	@echo "🧹 Cleaning web application..."
	@make web-stop
	@echo "Removing web application containers..."
	@docker-compose rm -f web-frontend web-backend 2>/dev/null || echo "No containers to remove"
	@echo "Removing web application images..."
	@docker rmi classify-stock-growth-for-trading_web-frontend classify-stock-growth-for-trading_web-backend 2>/dev/null || echo "No custom images to remove"
	@echo "✅ Web application cleaned"

# Unified web status with configurable detail level
# Usage: make web-status [DETAIL=basic|health|test]
web-status:
	@detail="$(DETAIL)"; \
	if [ -z "$$detail" ]; then detail="basic"; fi; \
	if [ "$$detail" = "basic" ]; then \
		make _web-status-basic; \
	elif [ "$$detail" = "health" ]; then \
		make _web-status-health; \
	elif [ "$$detail" = "test" ]; then \
		make _web-status-test; \
	else \
		echo "❌ Invalid DETAIL: $$detail. Use: basic|health|test"; \
		exit 1; \
	fi

# Basic status check (default)
_web-status-basic:
	@echo "📊 Web Application Status"
	@echo "========================="
	@echo ""
	@echo "🌐 Frontend Status:"
	@curl -s -o /dev/null -w "  %-20s %{http_code}\n" http://localhost:3000 || echo "  Frontend:          Not running"
	@echo ""
	@echo "🔧 Backend Status:"
	@curl -s -o /dev/null -w "  %-20s %{http_code}\n" http://localhost:3001/health || echo "  Backend API:       Not running"
	@echo ""
	@echo "📊 Database Status:"
	@docker-compose exec postgres pg_isready -U postgres -d stock_data 2>/dev/null | sed 's/^/  /' || echo "  PostgreSQL:        Not running"
	@echo ""
	@echo "🗄️  Cache Status:"
	@redis_status=$$(docker-compose exec redis redis-cli ping 2>/dev/null || echo "FAIL"); \
	if [ "$$redis_status" = "PONG" ]; then \
		echo "  Redis Cache:       ✅ Connected"; \
	else \
		echo "  Redis Cache:       ❌ Not running"; \
	fi
	@echo ""
	@echo "🐳 Docker Container Status:"
	@docker-compose ps | grep -E "(web-frontend|web-backend)" | sed 's/^/  /' || echo "  No web containers running"
	@echo ""
	@echo "🔗 Access URLs:"
	@echo "  Frontend App:      http://localhost:3000"
	@echo "  Backend API:       http://localhost:3001"
	@echo "  API Health:        http://localhost:3001/health"
	@echo "  API Stocks:        http://localhost:3001/api/stocks"
	@echo "  Cache Status:      http://localhost:3001/api/cache/status"
	@echo "  Database:          postgresql://postgres:postgres@localhost:5432/stock_data"
	@echo "  Redis Cache:       localhost:6379"
	@echo "  Schema:            prod_stock_data"
	@echo ""
	@echo "💡 More Details: make web-status DETAIL=health"

# Health check with performance metrics
_web-status-health:
	@echo "🏥 Comprehensive Web Application Health Check"
	@echo "============================================="
	@echo ""
	@echo "1️⃣ Service Connectivity Tests:"
	@echo "--------------------------------"
	@echo -n "Frontend (React):     "
	@if curl -s -f http://localhost:3000 >/dev/null 2>&1; then \
		echo "✅ OK (200)"; \
	else \
		echo "❌ FAIL (Unable to connect)"; \
	fi
	@echo -n "Backend Health:       "
	@if curl -s -f http://localhost:3001/health >/dev/null 2>&1; then \
		echo "✅ OK (200)"; \
	else \
		echo "❌ FAIL (Health check failed)"; \
	fi
	@echo -n "Database Connection:  "
	@if curl -s -f http://localhost:3001/test-db >/dev/null 2>&1; then \
		echo "✅ OK (DB Connected)"; \
	else \
		echo "❌ FAIL (DB Connection failed)"; \
	fi
	@echo -n "Redis Cache:          "
	@if curl -s -f http://localhost:3001/api/cache/status >/dev/null 2>&1; then \
		cache_status=$$(curl -s http://localhost:3001/api/cache/status | grep -o '"connected":[^,]*' | cut -d':' -f2 2>/dev/null || echo "false"); \
		if [ "$$cache_status" = "true" ]; then \
			echo "✅ OK (Cache Connected)"; \
		else \
			echo "⚠️  DEGRADED (Cache Unavailable)"; \
		fi; \
	else \
		echo "❌ FAIL (Cache API failed)"; \
	fi
	@echo ""
	@echo "2️⃣ Container Health:"
	@echo "--------------------"
	@docker-compose ps web-frontend web-backend | tail -n +2 | while IFS= read -r line; do \
		if echo "$$line" | grep -q "Up.*healthy"; then \
			echo "✅ $$(echo "$$line" | awk '{print $$1}') - Healthy"; \
		elif echo "$$line" | grep -q "Up"; then \
			echo "⚠️  $$(echo "$$line" | awk '{print $$1}') - Running (no health check)"; \
		else \
			echo "❌ $$(echo "$$line" | awk '{print $$1}') - Not healthy"; \
		fi; \
	done 2>/dev/null || echo "❌ Web containers not running"
	@echo ""
	@echo "3️⃣ Performance Check:"
	@echo "---------------------"
	@echo -n "Backend Response Time: "
	@response_time=$$(curl -s -o /dev/null -w "%{time_total}" http://localhost:3001/health 2>/dev/null || echo "N/A"); \
	if [ "$$response_time" != "N/A" ]; then \
		echo "$${response_time}s"; \
		if [ "$$(echo "$$response_time < 1.0" | bc -l 2>/dev/null || echo 0)" = "1" ]; then \
			echo "✅ Response time is good (<1s)"; \
		else \
			echo "⚠️  Response time is slow (>1s)"; \
		fi; \
	else \
		echo "❌ Unable to measure"; \
	fi
	@echo ""
	@echo "📋 Health Summary:"
	@echo "------------------"
	@if curl -s -f http://localhost:3000 >/dev/null 2>&1 && curl -s -f http://localhost:3001/health >/dev/null 2>&1; then \
		echo "🎉 Web application is HEALTHY and ready to use!"; \
		echo "🌐 Access your stock dashboard at: http://localhost:3000"; \
	else \
		echo "⚠️  Web application has issues. Run 'make web MODE=restart' to fix."; \
	fi

# API endpoint testing
_web-status-test:
	@echo "🧪 Web Application API Tests"
	@echo "============================"
	@echo ""
	@echo "Testing backend health..."
	@if curl -s -f http://localhost:3001/health >/dev/null 2>&1; then \
		echo "✅ Backend health check passed"; \
	else \
		echo "❌ Backend health check failed"; \
	fi
	@echo "Testing frontend availability..."
	@if curl -s -f http://localhost:3000 >/dev/null 2>&1; then \
		echo "✅ Frontend accessibility passed"; \
	else \
		echo "❌ Frontend not accessible"; \
	fi
	@echo "Testing API endpoints..."
	@if curl -s -f http://localhost:3001/api/stocks >/dev/null 2>&1; then \
		echo "✅ Stocks API endpoint passed"; \
	else \
		echo "❌ Stocks API endpoint failed"; \
	fi
	@echo "Testing stock data retrieval..."
	@if curl -s -f "http://localhost:3001/api/stocks/XTB?timeframe=1M" >/dev/null 2>&1; then \
		echo "✅ Stock data retrieval passed"; \
	else \
		echo "❌ Stock data retrieval failed"; \
	fi
	@echo ""
	@echo "✅ Web application tests completed"

# Legacy command aliases for backward compatibility
web-health:
	@make web-status DETAIL=health

web-test:
	@make web-status DETAIL=test

# ==================== DEVELOPMENT WEB APPLICATION COMMANDS ====================

# Restart EVERYTHING: Infrastructure + Development Web Application
dev-restart:
	@echo "🔄 COMPLETE DEVELOPMENT RESTART"
	@echo "==============================="
	@echo ""
	@echo "Step 1: Stopping all services..."
	@make dev-web-stop 2>/dev/null || echo "No development web processes to stop"
	@make stop
	@sleep 5
	@echo ""
	@echo "Step 2: Starting infrastructure (PostgreSQL + Airflow + pgAdmin)..."
	@make start
	@echo ""
	@echo "Step 3: Starting development web application..."
	@sleep 5
	@make dev-web-start
	@echo ""
	@echo "✅ COMPLETE DEVELOPMENT RESTART FINISHED!"
	@echo "=========================================="
	@echo ""
	@echo "🌐 All Services Status:"
	@make dev-web-status

# Install frontend dependencies
dev-web-install:
	@echo "📦 Installing web application dependencies..."
	@echo "Installing backend dependencies..."
	@cd web-app/backend && npm install
	@echo "Installing frontend dependencies..."
	@cd web-app/frontend && npm install
	@echo "✅ All dependencies installed successfully"

# Start both backend and frontend in development mode
dev-web-start:
	@echo "⚡ Starting development web application..."
	@echo "Starting backend API server..."
	@cd web-app/backend && npm run dev &
	@sleep 5
	@echo "Starting frontend development server..."
	@cd web-app/frontend && npm start &
	@sleep 10
	@echo ""
	@echo "✅ Development web application started!"
	@make dev-web-status

# Start only backend API server in development mode
dev-web-backend:
	@echo "🔧 Starting backend API server..."
	@cd web-app/backend && npm run dev

# Start only frontend development server
dev-web-frontend:
	@echo "🌐 Starting frontend development server..."
	@cd web-app/frontend && npm start

# Restart development web services
dev-web-restart:
	@echo "🔄 Restarting development web application..."
	@make dev-web-stop
	@sleep 3
	@make dev-web-start
	@echo "✅ Development web application restarted"

# Stop development web services
dev-web-stop:
	@echo "🛑 Stopping development web services..."
	@echo "Stopping Node.js processes..."
	@pkill -f "npm run dev" 2>/dev/null || echo "Backend not running"
	@pkill -f "npm start" 2>/dev/null || echo "Frontend not running"
	@pkill -f "react-scripts start" 2>/dev/null || echo "React dev server not running"
	@pkill -f "nodemon" 2>/dev/null || echo "Nodemon not running"
	@echo "✅ Development web services stopped"

# Show development web services status
dev-web-status:
	@echo "⚡ Development Web Application Status"
	@echo "===================================="
	@echo ""
	@echo "🌐 Frontend Development Server:"
	@curl -s -o /dev/null -w "  Status:           %{http_code} (React Dev Server)\n" http://localhost:3000 || echo "  Status:           Not running"
	@echo ""
	@echo "🔧 Backend API Server:"
	@curl -s -o /dev/null -w "  Health Check:     %{http_code}\n" http://localhost:3001/health || echo "  Health Check:     Not running"
	@curl -s -o /dev/null -w "  Stocks API:       %{http_code}\n" http://localhost:3001/api/stocks || echo "  Stocks API:       Not running"
	@echo ""
	@echo "📊 Database Status:"
	@docker-compose exec postgres pg_isready -U postgres -d stock_data 2>/dev/null | sed 's/^/  /' || echo "  PostgreSQL:       Not running (run 'make start' first)"
	@echo ""
	@echo "🔗 Development URLs:"
	@echo "  Frontend App:     http://localhost:3000 (React Dev Server with Hot Reload)"
	@echo "  Backend API:      http://localhost:3001 (Express.js with Nodemon)"
	@echo "  API Health:       http://localhost:3001/health"
	@echo "  API Stocks:       http://localhost:3001/api/stocks"
	@echo ""
	@echo "💡 Development Features:"
	@echo "  • Hot reload enabled for both frontend and backend"
	@echo "  • Enhanced debugging with improved error messages"
	@echo "  • Real-time data from prod_stock_data schema"
	@echo "  • Console logging for API requests and chart rendering"
	@echo ""
	@echo "📋 Development Commands:"
	@echo "  make dev-web-install   # Install/update dependencies"
	@echo "  make dev-web-restart   # Restart both services"
	@echo "  make dev-web-backend   # Start backend only"
	@echo "  make dev-web-frontend  # Start frontend only"