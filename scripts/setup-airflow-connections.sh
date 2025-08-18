#!/bin/bash

# Wait for Airflow to be ready
echo "Waiting for Airflow to be ready..."
sleep 10

# Check if Airflow is ready by testing the DB connection
while ! airflow db check 2>/dev/null; do
    echo "Airflow database not ready yet, waiting..."
    sleep 5
done

echo "Airflow is ready, setting up connections..."

# Setup database connections
echo "Setting up Airflow database connections..."

# Create postgres_default connection
airflow connections add postgres_default \
    --conn-type postgres \
    --conn-host postgres \
    --conn-schema stock_data \
    --conn-login stock \
    --conn-password stock \
    --conn-port 5432 2>/dev/null || echo "postgres_default connection already exists"

# Create postgres_stock connection
airflow connections add postgres_stock \
    --conn-type postgres \
    --conn-host postgres \
    --conn-schema stock_data \
    --conn-login stock \
    --conn-password stock \
    --conn-port 5432 2>/dev/null || echo "postgres_stock connection already exists"

echo "✅ Airflow connections configured"