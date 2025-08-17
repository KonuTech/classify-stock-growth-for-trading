"""Database connection and session management."""

import os
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import structlog

logger = structlog.get_logger(__name__)


class DatabaseConfig:
    """Database configuration management."""
    
    def __init__(self, schema: str = "test_stock_data"):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME", "stock_data")
        self.username = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")
        self.schema = schema
        
        # Connection pool settings
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
    @property
    def connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        return (
            f"postgresql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )
    
    def __repr__(self) -> str:
        return f"DatabaseConfig(host={self.host}, database={self.database}, schema={self.schema})"


class DatabaseManager:
    """Database connection manager with connection pooling."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        
    @property
    def engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.config.connection_string,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=os.getenv("DB_ECHO", "false").lower() == "true"
            )
            logger.info(
                "Database engine created",
                host=self.config.host,
                database=self.config.database,
                schema=self.config.schema
            )
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                expire_on_commit=False
            )
        return self._session_factory
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        session = self.session_factory()
        try:
            # Set the search path to include our schema
            session.execute(text(f"SET search_path TO {self.config.schema}, public"))
            session.commit()
            
            logger.debug("Database session created", schema=self.config.schema)
            yield session
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(
                "Database session error",
                error=str(e),
                schema=self.config.schema
            )
            raise
        finally:
            session.close()
            logger.debug("Database session closed")
    
    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1 as test")).fetchone()
                if result and result[0] == 1:
                    logger.info("Database connection test successful")
                    return True
                else:
                    logger.error("Database connection test failed - unexpected result")
                    return False
        except Exception as e:
            logger.error("Database connection test failed", error=str(e))
            return False
    
    def create_schema_if_not_exists(self) -> bool:
        """Create schema if it doesn't exist."""
        try:
            with self.get_session() as session:
                session.execute(text(
                    f"CREATE SCHEMA IF NOT EXISTS {self.config.schema}"
                ))
                session.commit()
                logger.info("Schema created or verified", schema=self.config.schema)
                return True
        except Exception as e:
            logger.error(
                "Failed to create schema",
                schema=self.config.schema,
                error=str(e)
            )
            return False
    
    def execute_sql_file(self, file_path: str) -> bool:
        """Execute SQL file with proper error handling and COMMIT support."""
        logger.info(
            "Starting SQL file execution",
            file_path=file_path,
            schema=self.config.schema,
            database=self.config.database
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Process as f-string for consistent handling
            sql_f_string = f"""{sql_content}"""
            
            logger.info(
                "SQL file loaded",
                file_size=len(sql_content),
                estimated_statements=len([s for s in sql_f_string.split(';') if s.strip()])
            )
            
            # Use raw connection to handle COMMIT statements properly
            connection = self.engine.raw_connection()
            try:
                cursor = connection.cursor()
                
                # Set search path first
                logger.info(f"Setting search path to {self.config.schema}")
                cursor.execute(f"SET search_path TO {self.config.schema}, public")
                logger.info("Search path set successfully")
                
                # Execute the entire SQL content as one f-string block
                sql_f_string = f"""{sql_content}"""
                
                # Execute as a single block instead of splitting statements
                try:
                    logger.info("Executing complete SQL block as f-string")
                    cursor.execute(sql_f_string)
                    connection.commit()
                    logger.info("Successfully executed complete SQL block")
                    return True
                except Exception as e:
                    logger.error(
                        "Failed to execute SQL block",
                        error=str(e),
                        error_type=type(e).__name__
                    )
                    connection.rollback()
                    return False
                
            finally:
                connection.close()
                
        except Exception as e:
            logger.error(
                "Failed to execute SQL file",
                file_path=file_path,
                error=str(e)
            )
            return False
    
    def close(self):
        """Close database connections."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connections closed")


# Global database managers for different schemas
_db_managers = {}

def get_database_manager(schema: str = "test_stock_data") -> DatabaseManager:
    """Get database manager instance (singleton per schema)."""
    if schema not in _db_managers:
        config = DatabaseConfig(schema=schema)
        _db_managers[schema] = DatabaseManager(config)
    return _db_managers[schema]


def get_dev_database() -> DatabaseManager:
    """Get development database manager."""
    return get_database_manager("dev_stock_data")


def get_test_database() -> DatabaseManager:
    """Get test database manager."""
    return get_database_manager("test_stock_data")


@contextmanager
def get_db_session(schema: str = "test_stock_data") -> Generator[Session, None, None]:
    """Convenience function to get database session."""
    db_manager = get_database_manager(schema)
    with db_manager.get_session() as session:
        yield session