"""
Centralized logging configuration for stock_ml module.
Ensures all logs are saved to project root ./logs/stock_ml/ regardless of execution context.
"""

import logging
from pathlib import Path
from typing import Optional


def _find_project_root() -> Path:
    """Find the project root directory by looking for CLAUDE.md marker file"""
    current_path = Path(__file__).resolve()
    for parent in [current_path] + list(current_path.parents):
        if (parent / "CLAUDE.md").exists():
            return parent
    # Fallback to current directory if CLAUDE.md not found
    return Path.cwd()


def setup_ml_logger(module_name: str, log_filename: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger for stock_ml modules with consistent configuration.
    
    Args:
        module_name: Name of the module (usually __name__)
        log_filename: Optional custom log filename (defaults to module name)
        
    Returns:
        Configured logger instance
    """
    # Determine log filename
    if log_filename is None:
        # Extract module name from full module path (e.g., 'stock_ml.feature_engineering' -> 'feature_engineering')
        log_filename = module_name.split('.')[-1] if '.' in module_name else module_name
    
    # Ensure .log extension
    if not log_filename.endswith('.log'):
        log_filename = f"{log_filename}.log"
    
    # Set up logging directory using absolute path
    project_root = _find_project_root()
    logs_dir = project_root / "logs" / "stock_ml"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(module_name)
    
    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(logs_dir / log_filename)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False
    
    return logger


def get_ml_logger(module_name: str) -> logging.Logger:
    """
    Get or create a logger for stock_ml modules.
    
    Args:
        module_name: Name of the module (usually __name__)
        
    Returns:
        Logger instance
    """
    return setup_ml_logger(module_name)