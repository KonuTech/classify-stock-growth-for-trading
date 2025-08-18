#!/bin/bash

# Script to extract all service credentials and save to .env file
# This runs after all containers start up

echo "Waiting for services to initialize..."
sleep 60

echo "Extracting service credentials..."

# Extract Airflow password from logs
AIRFLOW_PASSWORD=$(docker-compose logs airflow 2>/dev/null | grep "Password for user 'admin':" | tail -1 | sed -n "s/.*Password for user 'admin': \(.*\)/\1/p")

# Create or update .env file
if [ -f .env ]; then
    # Remove existing credentials if they exist
    sed -i '/^AIRFLOW_/d' .env
    sed -i '/^PGADMIN_/d' .env  
    sed -i '/^POSTGRES_/d' .env
fi

# Add all service credentials to .env
echo "# Service Credentials - Auto-generated $(date)" >> .env
echo "" >> .env

# Airflow credentials
if [ -n "$AIRFLOW_PASSWORD" ]; then
    echo "# Airflow - http://localhost:8080" >> .env
    echo "AIRFLOW_USERNAME=admin" >> .env
    echo "AIRFLOW_PASSWORD=$AIRFLOW_PASSWORD" >> .env
    echo "" >> .env
    echo "✓ Airflow credentials saved"
else
    echo "⚠ Could not extract Airflow password from logs"
fi

# pgAdmin credentials (from docker-compose.yml)
echo "# pgAdmin - http://localhost:5050" >> .env
echo "PGADMIN_EMAIL=admin@admin.com" >> .env
echo "PGADMIN_PASSWORD=admin" >> .env
echo "" >> .env

# PostgreSQL credentials (from docker-compose.yml)
echo "# PostgreSQL - localhost:5432" >> .env
echo "POSTGRES_HOST=localhost" >> .env
echo "POSTGRES_PORT=5432" >> .env
echo "POSTGRES_USER=postgres" >> .env
echo "POSTGRES_PASSWORD=postgres" >> .env
echo "POSTGRES_DB=stock_data" >> .env

echo ""
echo "=== ALL SERVICE CREDENTIALS ==="
echo "Airflow Web UI: http://localhost:8080"
echo "  Username: admin"
if [ -n "$AIRFLOW_PASSWORD" ]; then
    echo "  Password: $AIRFLOW_PASSWORD"
else
    echo "  Password: [Check logs manually]"
fi
echo ""
echo "pgAdmin Web UI: http://localhost:5050" 
echo "  Email: admin@admin.com"
echo "  Password: admin"
echo ""
echo "PostgreSQL Database: localhost:5432"
echo "  Username: postgres"
echo "  Password: postgres"
echo "  Database: stock_data"
echo ""
echo "All credentials saved to .env file"
echo "================================"