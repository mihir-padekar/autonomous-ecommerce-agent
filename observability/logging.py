import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """
    Formats log records into structured JSON objects for ingestion by
    modern log collectors (Datadog, CloudWatch, Grafana Loki, ELK).
    """

    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Include structured extra attributes if attached
        if hasattr(record, "thread_id"):
            log_payload["thread_id"] = record.thread_id
        if hasattr(record, "event"):
            log_payload["event"] = record.event
        if hasattr(record, "context"):
            log_payload["context"] = record.context

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload)


def setup_logger(name: str = "operations_copilot", level: int = logging.INFO) -> logging.Logger:
    """
    Initializes and returns a logger configured with structured JSON output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers on reload
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    logger.propagate = False
    return logger


# Global application logger
app_logger = setup_logger("ecommerce.operations")

