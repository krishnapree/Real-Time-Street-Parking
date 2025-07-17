"""
Logging configuration for the application
"""

import logging
import sys
from pathlib import Path
from loguru import logger


def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with consistent formatting
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    
    # Remove default loguru handler
    logger.remove()
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # Add file handler for errors
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # Add file handler for all logs
    logger.add(
        log_dir / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="INFO",
        rotation="1 day",
        retention="7 days",
        compression="zip"
    )
    
    # Create standard logger that uses loguru
    standard_logger = logging.getLogger(name)
    standard_logger.handlers = []
    standard_logger.addHandler(InterceptHandler())
    standard_logger.setLevel(logging.INFO)
    
    return standard_logger


class InterceptHandler(logging.Handler):
    """
    Handler to intercept standard logging and redirect to loguru
    """
    
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
