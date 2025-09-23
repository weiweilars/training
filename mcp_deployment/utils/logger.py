"""
Logging utilities for MCP Deployment
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class JSONFormatter(logging.Formatter):
    """JSON log formatter"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "user"):
            log_data["user"] = record.user

        return json.dumps(log_data)


def setup_logger(
    name: str,
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup logger with specified configuration"""

    logger = logging.getLogger(name)

    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers = []

    # Create formatter
    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class RequestLogger:
    """Logger with request context"""

    def __init__(self, logger: logging.Logger, request_id: str, user: Optional[dict] = None):
        self.logger = logger
        self.request_id = request_id
        self.user = user

    def _add_context(self, record):
        """Add request context to log record"""
        record.request_id = self.request_id
        if self.user:
            record.user = self.user

    def debug(self, message, *args, **kwargs):
        """Log debug message with context"""
        record = logging.LogRecord(
            self.logger.name, logging.DEBUG, "", 0,
            message, args, None
        )
        self._add_context(record)
        self.logger.handle(record)

    def info(self, message, *args, **kwargs):
        """Log info message with context"""
        record = logging.LogRecord(
            self.logger.name, logging.INFO, "", 0,
            message, args, None
        )
        self._add_context(record)
        self.logger.handle(record)

    def warning(self, message, *args, **kwargs):
        """Log warning message with context"""
        record = logging.LogRecord(
            self.logger.name, logging.WARNING, "", 0,
            message, args, None
        )
        self._add_context(record)
        self.logger.handle(record)

    def error(self, message, *args, **kwargs):
        """Log error message with context"""
        record = logging.LogRecord(
            self.logger.name, logging.ERROR, "", 0,
            message, args, None
        )
        self._add_context(record)
        self.logger.handle(record)