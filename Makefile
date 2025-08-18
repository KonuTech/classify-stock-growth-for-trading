.PHONY: start stop restart extract-credentials clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  make start              - Start all services and extract credentials"
	@echo "  make stop               - Stop all services"
	@echo "  make restart            - Restart all services and extract credentials"
	@echo "  make extract-credentials - Extract credentials to .env file"
	@echo "  make clean              - Stop services and clean up"
	@echo "  make help               - Show this help"

# Start services and extract credentials
start:
	@echo "Starting all services..."
	docker-compose up -d postgres pgadmin airflow
	@echo "Waiting for services to initialize..."
	@sleep 70
	@make extract-credentials

# Stop all services
stop:
	@echo "Stopping all services..."
	docker-compose down

# Restart services
restart: stop start

# Extract credentials from logs and save to .env
extract-credentials:
	@echo "Extracting service credentials..."
	@# Extract Airflow password from logs
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
	echo "POSTGRES_DB=stock_data" >> .env; \
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
	echo "PostgreSQL Database: localhost:5432"; \
	echo "  Username: postgres"; \
	echo "  Password: postgres"; \
	echo "  Database: stock_data"; \
	echo ""; \
	echo "All credentials saved to .env file"; \
	echo "================================"

# Clean up everything
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	@if [ -f .env ]; then rm .env; fi
	@echo "Cleanup complete"