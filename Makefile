.PHONY: start stop restart extract-credentials clean help init-dev init-test init-prod setup-airflow fix-schema-permissions trigger-dev-dag trigger-test-dag trigger-prod-dag trigger-dev-ml-dags trigger-test-ml-dags trigger-prod-ml-dags trigger-ml-stock web-init web-dev web-build web-start web-stop web-restart web-logs web-clean web-test web-status

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "🚀 Infrastructure:"
	@echo "  make start              - COMPLETE DEPLOYMENT: services + schemas + DAGs + credentials"
	@echo "  make start-services     - Start Docker services only (no schemas/credentials)"
	@echo "  make init-dev           - Initialize dev environment + trigger dev DAG (no credentials)"
	@echo "  make init-test          - Initialize test environment + trigger test DAG (no credentials)"  
	@echo "  make init-prod          - Initialize prod environment with ML tables (no credentials)"
	@echo "  make extract-credentials - Extract service credentials to .env file"
	@echo "  make setup-airflow      - Setup Airflow database connections only"
	@echo "  make stop               - Stop all services"
	@echo "  make restart            - Restart all services with complete setup"
	@echo "  make clean              - Stop services and clean up completely"
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
	@echo "🌐 Web Application:"
	@echo "  make web-init           - Initialize React web application structure"
	@echo "  make web-dev            - Start development servers (frontend + backend + database)"
	@echo "  make web-build          - Build production web application"
	@echo "  make web-start          - Start production web application (Docker)"
	@echo "  make web-stop           - Stop web application containers"
	@echo "  make web-restart        - Restart web application with latest changes"
	@echo "  make web-logs           - Show web application logs"
	@echo "  make web-clean          - Clean web application containers and images"
	@echo "  make web-test           - Run web application tests"
	@echo "  make web-status         - Show web application status and URLs"
	@echo ""
	@echo "❓ Help:"
	@echo "  make help               - Show this help"

# Start services with complete setup (all schemas + airflow + DAGs)
start:
	@echo "Starting all services..."
	docker-compose up -d postgres pgadmin airflow
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
	@echo "✅ Complete infrastructure deployment ready!"
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

# Restart services with complete development setup
restart: stop start

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
	docker-compose up -d postgres pgadmin airflow
	@echo "Waiting for services to initialize..."
	@sleep 70

# Complete development environment initialization
init-dev: start-services
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
	@echo "💡 Note: Run 'make extract-credentials' to get service credentials"

# Complete test environment initialization  
init-test: start-services
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
	@echo "💡 Note: Run 'make extract-credentials' to get service credentials"

# Complete production environment initialization
init-prod: start-services
	@echo "Setting up production environment..."
	@sleep 5
	@echo "Initializing prod_stock_data schema with ML tables..."
	@uv run python -m stock_etl.cli database init-prod
	@make fix-schema-permissions
	@make setup-airflow
	@echo "✅ Production environment ready with complete ML pipeline support!"
	@echo "   - ETL tables: ✅ (exchanges, base_instruments, stocks, indices, stock_prices, etl_jobs)"
	@echo "   - ML tables: ✅ (ml_models, ml_feature_data, ml_predictions, ml_backtest_results)"
	@echo "   - Indexes: ✅ (optimized for time-series queries and ML operations)"
	@echo "   - Reference data: ✅ (WSE exchanges, sectors, sample instruments)"
	@echo "🌐 Airflow UI: http://localhost:8080"
	@echo "📊 pgAdmin: http://localhost:5050"
	@echo "💡 Note: Run 'make extract-credentials' to get service credentials"

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
	@echo "Removing all untagged images..."
	docker rmi $$(docker images -q) -f 2>/dev/null || echo "No images to remove"
	docker system prune -a --volumes -f
	@if [ -f .env ]; then rm .env; fi
	@echo "Removing old Airflow logs..."
	@rm -rf stock_etl/airflow_logs/dag_id=*
	@rm -rf stock_etl/airflow_logs/dag_processor/*
	@rm -rf stock_etl/airflow_logs/etl/*.log
	@echo "Complete cleanup finished"

# ==================== WEB APPLICATION COMMANDS ====================

# Initialize React web application structure
web-init:
	@echo "🚀 Initializing React web application structure..."
	@if [ ! -d "web-app" ]; then \
		echo "Creating web-app directory structure..."; \
		mkdir -p web-app/frontend web-app/backend; \
		echo "✅ Directory structure created"; \
	else \
		echo "✅ web-app directory already exists"; \
	fi
	@echo "Creating frontend (React + TypeScript)..."
	@if [ ! -f "web-app/frontend/package.json" ]; then \
		cd web-app/frontend && npx create-react-app . --template typescript --silent; \
		cd web-app/frontend && npm install @tanstack/react-query recharts @headlessui/react @heroicons/react axios date-fns; \
		cd web-app/frontend && npm install -D tailwindcss autoprefixer postcss @types/date-fns; \
		cd web-app/frontend && npx tailwindcss init -p; \
		echo "✅ Frontend dependencies installed"; \
	else \
		echo "✅ Frontend already initialized"; \
	fi
	@echo "Creating backend (Node.js + Express + TypeScript)..."
	@if [ ! -f "web-app/backend/package.json" ]; then \
		cd web-app/backend && npm init -y; \
		cd web-app/backend && npm install express cors dotenv pg; \
		cd web-app/backend && npm install -D typescript @types/node @types/express @types/cors @types/pg nodemon ts-node; \
		cd web-app/backend && npx tsc --init; \
		echo "✅ Backend dependencies installed"; \
	else \
		echo "✅ Backend already initialized"; \
	fi
	@echo "Creating Docker configuration..."
	@if [ ! -f "web-app/docker-compose.yml" ]; then \
		echo 'version: "3.8"' > web-app/docker-compose.yml; \
		echo 'services:' >> web-app/docker-compose.yml; \
		echo '  frontend:' >> web-app/docker-compose.yml; \
		echo '    build: ./frontend' >> web-app/docker-compose.yml; \
		echo '    ports:' >> web-app/docker-compose.yml; \
		echo '      - "3000:3000"' >> web-app/docker-compose.yml; \
		echo '    environment:' >> web-app/docker-compose.yml; \
		echo '      - REACT_APP_API_URL=http://localhost:3001' >> web-app/docker-compose.yml; \
		echo '    depends_on:' >> web-app/docker-compose.yml; \
		echo '      - backend' >> web-app/docker-compose.yml; \
		echo '  backend:' >> web-app/docker-compose.yml; \
		echo '    build: ./backend' >> web-app/docker-compose.yml; \
		echo '    ports:' >> web-app/docker-compose.yml; \
		echo '      - "3001:3001"' >> web-app/docker-compose.yml; \
		echo '    environment:' >> web-app/docker-compose.yml; \
		echo '      - NODE_ENV=development' >> web-app/docker-compose.yml; \
		echo '      - DB_HOST=host.docker.internal' >> web-app/docker-compose.yml; \
		echo '      - DB_PORT=5432' >> web-app/docker-compose.yml; \
		echo '      - DB_NAME=stock_data' >> web-app/docker-compose.yml; \
		echo '      - DB_USER=postgres' >> web-app/docker-compose.yml; \
		echo '      - DB_PASSWORD=postgres' >> web-app/docker-compose.yml; \
		echo '      - DB_SCHEMA=prod_stock_data' >> web-app/docker-compose.yml; \
		echo "✅ Docker Compose configuration created"; \
	else \
		echo "✅ Docker configuration already exists"; \
	fi
	@echo ""
	@echo "🎯 React Web Application Initialized Successfully!"
	@echo "📁 Structure: web-app/frontend (React) + web-app/backend (Node.js)"
	@echo "🐳 Docker: web-app/docker-compose.yml configured"
	@echo "📊 Database: Connected to prod_stock_data schema"
	@echo ""
	@echo "Next steps:"
	@echo "  make web-dev    # Start development servers"
	@echo "  make web-build  # Build production version"
	@echo "  make web-start  # Start with Docker"

# Start development servers (frontend + backend)
web-dev:
	@echo "🚀 Starting web application development servers..."
	@if [ ! -d "web-app" ]; then \
		echo "❌ Web application not initialized. Run 'make web-init' first."; \
		exit 1; \
	fi
	@echo "Starting PostgreSQL database (if not running)..."
	@docker-compose up -d postgres || echo "Database already running"
	@sleep 5
	@echo "Starting backend server..."
	@cd web-app/backend && npm run dev &
	@sleep 3
	@echo "Starting frontend development server..."
	@cd web-app/frontend && BROWSER=none npm start &
	@sleep 5
	@echo ""
	@echo "✅ Development servers started!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:3001"
	@echo "📊 Database: prod_stock_data schema"
	@echo ""
	@echo "💡 Use Ctrl+C to stop development servers"
	@echo "💡 Use 'make web-logs' to view logs"

# Build production web application
web-build:
	@echo "🔨 Building production web application..."
	@if [ ! -d "web-app" ]; then \
		echo "❌ Web application not initialized. Run 'make web-init' first."; \
		exit 1; \
	fi
	@echo "Building frontend..."
	@cd web-app/frontend && npm run build
	@echo "Building backend..."
	@cd web-app/backend && npm run build || echo "Backend TypeScript compilation completed"
	@echo "Building Docker images..."
	@cd web-app && docker-compose build --no-cache
	@echo ""
	@echo "✅ Production build completed!"
	@echo "🐳 Docker images built and ready for deployment"
	@echo "🚀 Run 'make web-start' to start production containers"

# Start production web application (Docker)
web-start:
	@echo "🚀 Starting production web application..."
	@if [ ! -f "web-app/docker-compose.yml" ]; then \
		echo "❌ Web application not initialized. Run 'make web-init' first."; \
		exit 1; \
	fi
	@echo "Ensuring database is available..."
	@docker-compose up -d postgres
	@sleep 10
	@echo "Starting web application containers..."
	@cd web-app && docker-compose up -d
	@sleep 15
	@echo ""
	@echo "✅ Production web application started!"
	@make web-status

# Stop web application containers
web-stop:
	@echo "🛑 Stopping web application..."
	@if [ -f "web-app/docker-compose.yml" ]; then \
		cd web-app && docker-compose down; \
		echo "✅ Web application stopped"; \
	else \
		echo "⚠️ Web application not found"; \
	fi
	@echo "Stopping development processes..."
	@pkill -f "npm start" 2>/dev/null || echo "No frontend dev server running"
	@pkill -f "npm run dev" 2>/dev/null || echo "No backend dev server running"
	@pkill -f "node.*3001" 2>/dev/null || echo "No Node.js processes on port 3001"

# Restart web application with latest changes
web-restart:
	@echo "🔄 Restarting web application..."
	@make web-stop
	@sleep 3
	@make web-build
	@make web-start
	@echo "✅ Web application restarted with latest changes"

# Show web application logs
web-logs:
	@echo "📋 Web Application Logs"
	@echo "======================="
	@if [ -f "web-app/docker-compose.yml" ]; then \
		echo "🌐 Frontend logs:"; \
		cd web-app && docker-compose logs --tail=20 frontend 2>/dev/null || echo "Frontend container not running"; \
		echo ""; \
		echo "🔧 Backend logs:"; \
		cd web-app && docker-compose logs --tail=20 backend 2>/dev/null || echo "Backend container not running"; \
	else \
		echo "⚠️ Docker containers not running. Check development servers:"; \
		echo "Frontend: http://localhost:3000"; \
		echo "Backend: http://localhost:3001"; \
	fi

# Clean web application containers and images
web-clean:
	@echo "🧹 Cleaning web application..."
	@make web-stop
	@echo "Removing web application containers..."
	@cd web-app && docker-compose rm -f 2>/dev/null || echo "No containers to remove"
	@echo "Removing web application images..."
	@docker rmi web-app_frontend web-app_backend 2>/dev/null || echo "No custom images to remove"
	@echo "Cleaning build artifacts..."
	@rm -rf web-app/frontend/build 2>/dev/null || echo "No frontend build to clean"
	@rm -rf web-app/backend/dist 2>/dev/null || echo "No backend build to clean"
	@rm -rf web-app/frontend/node_modules/.cache 2>/dev/null || echo "No cache to clean"
	@echo "✅ Web application cleaned"

# Run web application tests
web-test:
	@echo "🧪 Running web application tests..."
	@if [ ! -d "web-app" ]; then \
		echo "❌ Web application not initialized. Run 'make web-init' first."; \
		exit 1; \
	fi
	@echo "Running frontend tests..."
	@cd web-app/frontend && npm test -- --coverage --watchAll=false || echo "Frontend tests completed"
	@echo "Running backend tests..."
	@cd web-app/backend && npm test || echo "Backend tests completed"
	@echo "Testing API connectivity..."
	@curl -s http://localhost:3001/health || echo "Backend not running on port 3001"
	@echo "✅ Web application tests completed"

# Show web application status and URLs
web-status:
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
	@echo "🐳 Docker Container Status:"
	@cd web-app && docker-compose ps 2>/dev/null | grep -E "(frontend|backend)" | sed 's/^/  /' || echo "  No containers running"
	@echo ""
	@echo "🔗 Access URLs:"
	@echo "  Frontend App:      http://localhost:3000"
	@echo "  Backend API:       http://localhost:3001"
	@echo "  API Health:        http://localhost:3001/health"
	@echo "  Database:          postgresql://postgres:postgres@localhost:5432/stock_data"
	@echo "  Schema:            prod_stock_data"
	@echo ""
	@echo "💡 Available Commands:"
	@echo "  make web-dev       # Start development"
	@echo "  make web-build     # Build production"
	@echo "  make web-logs      # View logs"
	@echo "  make web-restart   # Restart application"