.PHONY: start stop restart extract-credentials clean help init-dev init-test init-prod setup-airflow fix-schema-permissions trigger-dev-dag trigger-test-dag trigger-prod-dag

# Default target
help:
	@echo "Available commands:"
	@echo "  make start              - 🚀 COMPLETE DEPLOYMENT: services + schemas + DAGs (recommended)"
	@echo "  make init-dev           - Initialize dev environment + trigger dev DAG"
	@echo "  make init-test          - Initialize test environment + trigger test DAG"  
	@echo "  make init-prod          - Initialize prod environment + trigger prod DAG"
	@echo "  make setup-airflow      - Setup Airflow database connections only"
	@echo "  make trigger-dev-dag    - Trigger development ETL DAG"
	@echo "  make trigger-test-dag   - Trigger test ETL DAG"
	@echo "  make trigger-prod-dag   - Trigger production ETL DAG"
	@echo "  make stop               - Stop all services"
	@echo "  make restart            - Restart all services with complete setup"
	@echo "  make extract-credentials - Extract credentials to .env file"
	@echo "  make clean              - Stop services and clean up (removes logs)"
	@echo "  make help               - Show this help"

# Start services with complete setup (all schemas + airflow + DAGs)
start:
	@echo "Starting all services..."
	docker-compose up -d postgres pgadmin airflow
	@echo "Waiting for services to initialize..."
	@sleep 70
	@make extract-credentials
	@echo "Setting up all database schemas..."
	@sleep 5
	@echo "Initializing dev_stock_data schema..."
	@uv run python -m stock_etl.cli database init-dev
	@echo "Initializing test_stock_data schema..."
	@uv run python -m stock_etl.cli database init-test
	@echo "Production schema setup (manual for now)..."
	@echo "⚠️  Production schema initialization not yet implemented"
	@echo "    Use: uv run python -m stock_etl.cli database init-prod (when available)"
	@make fix-schema-permissions
	@make setup-airflow
	@echo "✅ All schemas initialized and permissions set!"
	@echo "Triggering all environment DAGs..."
	@make trigger-dev-dag
	@make trigger-test-dag
	@echo "⚠️  Production DAG not triggered (schema not initialized)"
	@echo "✅ Complete infrastructure deployment ready!"
	@echo "📊 Schemas: dev_stock_data ✅ test_stock_data ✅ prod_stock_data (manual)"
	@echo "🚀 DAGs: dev_stock_etl_pipeline ✅ test_stock_etl_pipeline ✅"
	@echo "🌐 Airflow UI: http://localhost:8080"
	@echo "📊 pgAdmin: http://localhost:5050"

# Stop all services
stop:
	@echo "Stopping all services..."
	docker-compose down

# Restart services with complete development setup
restart: stop start

# Rebuild Airflow service with dependencies (for DAG fixes)
restart-airflow:
	@echo "Stopping and rebuilding Airflow service..."
	docker-compose stop airflow
	docker-compose rm -f airflow
	docker-compose up -d airflow
	@echo "Airflow restarted with updated dependencies"

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

# Complete development environment initialization
init-dev: start
	@echo "Setting up development environment..."
	@sleep 5
	@echo "Initializing dev_stock_data schema..."
	@uv run python -m stock_etl.cli database init-dev
	@make fix-schema-permissions
	@make setup-airflow
	@echo "✅ Development environment ready!"
	@echo "Triggering development DAG..."
	@make trigger-dev-dag
	@echo "🌐 Airflow UI: http://localhost:8080"
	@echo "📊 pgAdmin: http://localhost:5050"

# Complete test environment initialization  
init-test: start
	@echo "Setting up test environment..."
	@sleep 5
	@echo "Initializing test_stock_data schema..."
	@uv run python -m stock_etl.cli database init-test
	@make fix-schema-permissions
	@make setup-airflow
	@echo "✅ Test environment ready!"
	@echo "Triggering test DAG..."
	@make trigger-test-dag
	@echo "🌐 Airflow UI: http://localhost:8080"
	@echo "📊 pgAdmin: http://localhost:5050"

# Complete production environment initialization
init-prod: start
	@echo "Setting up production environment..."
	@sleep 5
	@echo "Initializing prod_stock_data schema..."
	@echo "⚠️  Production schema initialization not yet implemented"
	@echo "    Use: uv run python -m stock_etl.cli database init-prod (when available)"
	@make setup-airflow
	@echo "✅ Production environment infrastructure ready!"
	@echo "🌐 Airflow UI: http://localhost:8080"
	@echo "📊 pgAdmin: http://localhost:5050"

# Fix schema permissions for Airflow database user
fix-schema-permissions:
	@echo "Fixing database schema permissions for Airflow user..."
	@docker-compose exec postgres psql -U postgres -d stock_data -c "GRANT USAGE ON SCHEMA dev_stock_data TO stock; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dev_stock_data TO stock; GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA dev_stock_data TO stock; ALTER DEFAULT PRIVILEGES IN SCHEMA dev_stock_data GRANT ALL ON TABLES TO stock; ALTER DEFAULT PRIVILEGES IN SCHEMA dev_stock_data GRANT ALL ON SEQUENCES TO stock;"
	@docker-compose exec postgres psql -U postgres -d stock_data -c "GRANT USAGE ON SCHEMA test_stock_data TO stock; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA test_stock_data TO stock; GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA test_stock_data TO stock; ALTER DEFAULT PRIVILEGES IN SCHEMA test_stock_data GRANT ALL ON TABLES TO stock; ALTER DEFAULT PRIVILEGES IN SCHEMA test_stock_data GRANT ALL ON SEQUENCES TO stock;"
	@echo "✅ Schema permissions fixed for Airflow database user"

# Setup Airflow database connections (now automated in docker-compose)
setup-airflow:
	@echo "Airflow connections are automatically configured via docker-compose"
	@echo "Waiting for connection setup to complete..."
	@sleep 10
	@echo "Verifying connections..."
	@docker-compose exec airflow airflow connections get postgres_default 2>/dev/null && echo "✅ postgres_default connection exists" || echo "⚠ postgres_default connection not found - checking logs..."
	@docker-compose exec airflow airflow connections get postgres_stock 2>/dev/null && echo "✅ postgres_stock connection exists" || echo "⚠ postgres_stock connection not found - checking logs..."

# Trigger environment-specific DAGs
trigger-dev-dag:
	@echo "Triggering development DAG..."
	@docker-compose exec airflow airflow dags trigger dev_stock_etl_pipeline
	@echo "✅ Development DAG triggered"

trigger-test-dag:
	@echo "Triggering test DAG..."
	@docker-compose exec airflow airflow dags trigger test_stock_etl_pipeline
	@echo "✅ Test DAG triggered"

trigger-prod-dag:
	@echo "Triggering production DAG..."
	@docker-compose exec airflow airflow dags trigger prod_stock_etl_pipeline
	@echo "✅ Production DAG triggered"

# Clean up everything
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	@if [ -f .env ]; then rm .env; fi
	@echo "Removing old Airflow logs..."
	@rm -rf stock_etl/airflow_logs/dag_id=*
	@rm -rf stock_etl/airflow_logs/dag_processor/*
	@rm -rf stock_etl/airflow_logs/etl/*.log
	@echo "Cleanup complete"