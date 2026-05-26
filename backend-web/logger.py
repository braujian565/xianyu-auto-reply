"""Logging configuration for xianyu-auto-reply backend."""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


# Using a more compact format for personal use — easier to read in terminal
DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
)
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str,
    level: str = "DEBUG",  # changed from INFO to DEBUG for easier local development
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
) -> logging.Logger:
    """
    Set up and return a configured logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module).
        level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path to a log file. If None, logs to stdout only.
        max_bytes: Maximum size of a single log file before rotation.
        backup_count: Number of rotated log files to keep.
        log_format: Log message format string.
        date_format: Date/time format string.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Console handler — always present
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler — optional
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent log records from propagating to the root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Retrieve an existing logger by name.

    If the logger has not been set up via `setup_logger` yet, a basic
    default configuration is applied so callers always get a usable logger.

    Args:
        name: Logger name.

    Returns:
        logging.Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Fallback: basic setup so the logger is immediately usable
        return setup_logger(name)
    return logger
