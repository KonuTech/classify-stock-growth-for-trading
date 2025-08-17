#!/usr/bin/env python3
"""Test script for the ETL pipeline."""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from stock_etl.cli import main

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ.setdefault("DB_HOST", "localhost")
    os.environ.setdefault("DB_PORT", "5432")
    os.environ.setdefault("DB_NAME", "stock_data")
    os.environ.setdefault("DB_USER", "postgres")
    os.environ.setdefault("DB_PASSWORD", "postgres")
    
    # Run the CLI
    main()