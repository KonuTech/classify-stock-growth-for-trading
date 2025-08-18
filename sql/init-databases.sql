-- Database initialization script for separate Airflow and business databases
-- This follows Developer A's approach: separate operational from transactional data

-- Create separate databases with appropriate ownership
CREATE DATABASE airflow_metadata
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TEMPLATE = template0
       LC_COLLATE = 'en_US.utf8'
       LC_CTYPE = 'en_US.utf8';

CREATE DATABASE stock_data
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TEMPLATE = template0
       LC_COLLATE = 'en_US.utf8'
       LC_CTYPE = 'en_US.utf8';

-- Create dedicated users for each database for better security separation
CREATE USER airflow WITH PASSWORD 'airflow';
CREATE USER stock WITH PASSWORD 'stock';

-- Grant appropriate permissions
GRANT ALL PRIVILEGES ON DATABASE airflow_metadata TO airflow;
GRANT ALL PRIVILEGES ON DATABASE stock_data TO stock;

-- Also grant to postgres user for administrative tasks
GRANT ALL PRIVILEGES ON DATABASE airflow_metadata TO postgres;
GRANT ALL PRIVILEGES ON DATABASE stock_data TO postgres;

-- Connect to each database and set up schemas
\c airflow_metadata;
COMMENT ON DATABASE airflow_metadata IS 'Airflow operational metadata and DAG execution history';

-- Create dedicated schema for Airflow metadata
CREATE SCHEMA IF NOT EXISTS airflow;
COMMENT ON SCHEMA airflow IS 'Airflow operational tables and metadata';

-- Grant full permissions to airflow user on their schema
GRANT ALL ON SCHEMA airflow TO airflow;
GRANT ALL ON ALL TABLES IN SCHEMA airflow TO airflow;
GRANT ALL ON ALL SEQUENCES IN SCHEMA airflow TO airflow;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA airflow TO airflow;

-- Set default privileges for future objects in airflow schema
ALTER DEFAULT PRIVILEGES IN SCHEMA airflow GRANT ALL ON TABLES TO airflow;
ALTER DEFAULT PRIVILEGES IN SCHEMA airflow GRANT ALL ON SEQUENCES TO airflow;
ALTER DEFAULT PRIVILEGES IN SCHEMA airflow GRANT ALL ON FUNCTIONS TO airflow;

\c stock_data;
COMMENT ON DATABASE stock_data IS 'Business data for stock market information from Stooq API';

-- Create schemas in stock_data for better organization
CREATE SCHEMA IF NOT EXISTS dev_stock_data;
CREATE SCHEMA IF NOT EXISTS test_stock_data;
CREATE SCHEMA IF NOT EXISTS prod_stock_data;

-- Grant schema permissions
GRANT ALL ON SCHEMA dev_stock_data TO stock, postgres;
GRANT ALL ON SCHEMA test_stock_data TO stock, postgres;
GRANT ALL ON SCHEMA prod_stock_data TO stock, postgres;

COMMENT ON SCHEMA dev_stock_data IS 'Development environment stock data with dummy data';
COMMENT ON SCHEMA test_stock_data IS 'Test environment stock data for automated testing';
COMMENT ON SCHEMA prod_stock_data IS 'Production stock data from Stooq API';

-- Return to default database
\c postgres;