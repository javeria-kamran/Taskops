"""
Logging Configuration (Phase III)

[FROM TASKS]: T002 - Setup Logging
[FROM PLAN]: Phase 1 - Setup

Structured JSON logging for production.
"""

import logging
import json
from typing import Any

logger = logging.getLogger(__name__)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(debug: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        debug: Enable debug logging
    """
    level = logging.DEBUG if debug else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = JSONFormatter()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logger.info("Logging configured", extra={"debug": debug})
