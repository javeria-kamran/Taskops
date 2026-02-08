"""
Structured JSON Logging Configuration
Provides centralized logging with JSON format, request context, and security filtering.
"""

import json
import logging
import logging.handlers
import os
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


class SensitiveDataFilter(logging.Filter):
    """Filter to remove sensitive data from logs."""

    SENSITIVE_KEYS = {
        "password", "secret", "token", "api_key", "apikey",
        "authorization", "jwt", "bearer", "aws_access_key",
        "aws_secret_key", "credit_card", "ssn", "api_secret",
        "refresh_token", "access_token"
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter sensitive data from log record."""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._redact_sensitive_data(record.msg)
        return True

    @staticmethod
    def _redact_sensitive_data(data: str) -> str:
        """Redact sensitive values from string."""
        if not isinstance(data, str):
            return data

        # Redact common patterns
        import re
        # SK_ prefixed keys (OpenAI keys)
        data = re.sub(r'sk-[a-zA-Z0-9]+', 'sk-***', data)
        # Bearer tokens
        data = re.sub(r'Bearer [a-zA-Z0-9_-]+', 'Bearer ***', data)
        # Passwords in URLs
        data = re.sub(
            r'(postgresql://[^:]+:)[^@]+(@)',
            r'\1***\2',
            data
        )
        return data


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def __init__(self, environment: str, version: str):
        super().__init__()
        self.environment = environment
        self.version = version

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
            "environment": self.environment,
            "version": self.version,
        }

        # Add optional fields if present
        if hasattr(record, "user_id") and record.user_id:
            # Anonymize user_id: show only first 8 chars
            user_id_str = str(record.user_id)
            anonymized = user_id_str[:8] + "-****-****-****" if len(user_id_str) > 8 else user_id_str
            log_data["user_id"] = anonymized

        if hasattr(record, "request_id") and record.request_id:
            log_data["request_id"] = record.request_id

        if hasattr(record, "duration_ms") and record.duration_ms is not None:
            log_data["duration_ms"] = record.duration_ms

        if hasattr(record, "status_code") and record.status_code is not None:
            log_data["status_code"] = record.status_code

        if hasattr(record, "path") and record.path:
            log_data["path"] = record.path

        # Add exception info if present
        if record.exc_info:
            log_data["error_type"] = record.exc_info[0].__name__
            log_data["error_details"] = "".join(
                traceback.format_exception(*record.exc_info)
            )

        return json.dumps(log_data, default=str)


class ContextualLogger:
    """Wrapper around logger to provide context-aware logging."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._context: Dict[str, Any] = {}

    def set_context(self, **kwargs):
        """Set logging context (user_id, request_id, etc.)."""
        self._context.update(kwargs)

    def clear_context(self):
        """Clear logging context."""
        self._context.clear()

    def _log_with_context(self, method: str, *args, **kwargs):
        """Log with context attached."""
        for key, value in self._context.items():
            kwargs.setdefault("extra", {})[key] = value
        getattr(self.logger, method)(*args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        """Log debug message with context."""
        self._log_with_context("debug", msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log info message with context."""
        self._log_with_context("info", msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log warning message with context."""
        self._log_with_context("warning", msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log error message with context."""
        self._log_with_context("error", msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log critical message with context."""
        self._log_with_context("critical", msg, *args, **kwargs)


# Global logger storage
_loggers: Dict[str, ContextualLogger] = {}
_is_configured = False


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
    environment: str = "production",
    version: str = "1.0.0",
) -> None:
    """
    Initialize logging configuration based on environment variables.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   Defaults to env var LOG_LEVEL or "INFO"
        log_format: Log format ("json" or "text")
                    Defaults to env var LOG_FORMAT or "json"
        log_file: Optional log file path
                  Defaults to env var LOG_FILE
        environment: Environment name (production, staging, development)
        version: Application version
    """
    global _is_configured

    if _is_configured:
        return

    # Get configuration from env vars or use defaults
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
    log_format = log_format or os.getenv("LOG_FORMAT", "json")
    log_file = log_file or os.getenv("LOG_FILE", None)
    environment = environment or os.getenv("ENVIRONMENT", "production")

    # Convert string level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    if log_format.lower() == "json":
        formatter = JSONFormatter(environment=environment, version=version)
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(SensitiveDataFilter())
        root_logger.addHandler(file_handler)

    root_logger.setLevel(level)
    _is_configured = True


def get_logger(name: str) -> ContextualLogger:
    """
    Get a named logger with context support.

    Args:
        name: Logger name (typically __name__)

    Returns:
        ContextualLogger instance
    """
    if name not in _loggers:
        base_logger = logging.getLogger(name)
        _loggers[name] = ContextualLogger(base_logger)
    return _loggers[name]


def log_request(
    logger: ContextualLogger,
    user_id: Optional[str],
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
) -> None:
    """
    Log HTTP request with context.

    Args:
        logger: ContextualLogger instance
        user_id: User ID (optional)
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
    """
    message = f"{method} {path} {status_code}"

    log_data = {
        "extra": {
            "duration_ms": round(duration_ms, 2),
            "status_code": status_code,
            "path": path,
        }
    }

    if user_id:
        log_data["extra"]["user_id"] = user_id

    # Determine log level based on status code
    if 200 <= status_code < 300:
        logger.info(message, **log_data)
    elif 300 <= status_code < 400:
        logger.info(message, **log_data)
    elif 400 <= status_code < 500:
        logger.warning(message, **log_data)
    else:
        logger.error(message, **log_data)


def log_error(
    logger: ContextualLogger,
    error: Exception,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """
    Log exception with context.

    Args:
        logger: ContextualLogger instance
        error: Exception to log
        user_id: User ID (optional)
        request_id: Request ID (optional)
    """
    log_data = {"extra": {}}

    if user_id:
        log_data["extra"]["user_id"] = user_id

    if request_id:
        log_data["extra"]["request_id"] = request_id

    logger.error(
        f"{error.__class__.__name__}: {str(error)}",
        exc_info=True,
        **log_data
    )


# Auto-initialize on module import
if not _is_configured and os.getenv("ENVIRONMENT") == "production":
    setup_logging()
