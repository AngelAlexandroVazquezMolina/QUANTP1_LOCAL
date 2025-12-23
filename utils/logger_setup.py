"""QUANTP1 v3.1 - Logger Setup with Rotation"""
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
import sys
from datetime import datetime
from config.paths_config import LOGS_DIR

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(name="quantp1", level=logging.INFO):
    """
    Setup logger with console and file handlers
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console Handler (INFO level, colored)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # System Log Handler (Daily rotation, INFO level)
    system_log = LOGS_DIR / "system.log"
    system_handler = TimedRotatingFileHandler(
        system_log,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    system_handler.setLevel(logging.INFO)
    system_format = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    system_handler.setFormatter(system_format)
    logger.addHandler(system_handler)
    
    # Error Log Handler (ERROR level only)
    error_log = LOGS_DIR / "error.log"
    error_handler = RotatingFileHandler(
        error_log,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(system_format)
    logger.addHandler(error_handler)
    
    # Trading Log Handler (DEBUG level, all trading operations)
    trading_log = LOGS_DIR / "trading.log"
    trading_handler = TimedRotatingFileHandler(
        trading_log,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    trading_handler.setLevel(logging.DEBUG)
    trading_format = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    trading_handler.setFormatter(trading_format)
    logger.addHandler(trading_handler)
    
    return logger


def get_logger(name="quantp1"):
    """Get existing logger or create new one"""
    return logging.getLogger(name)


if __name__ == "__main__":
    # Test logger
    logger = setup_logger()
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    print(f"\n✅ Logs written to: {LOGS_DIR}")
