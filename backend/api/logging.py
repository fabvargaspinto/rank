import json
import logging
from datetime import UTC, datetime

_STANDARD_RECORD_KEYS = frozenset(logging.makeLogRecord({}).__dict__) | {
    "message",
    "asctime",
    "taskName",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "time": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key in _STANDARD_RECORD_KEYS or key.startswith("_"):
                continue
            payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


class HealthAccessFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        if isinstance(args, tuple) and len(args) >= 3 and isinstance(args[2], str):
            path = args[2].split("?", 1)[0]
            if path == "/health":
                return False
        return " /health " not in f" {record.getMessage()} "


def configure_logging() -> None:
    formatter = JsonFormatter()
    root = logging.getLogger()
    if not root.handlers:
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        root.addHandler(stream)
    else:
        for existing in root.handlers:
            existing.setFormatter(formatter)
    root.setLevel(logging.INFO)

    # httpx loguea URLs completas; Meta manda tokens en query string.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        for existing in logger.handlers:
            existing.setFormatter(formatter)
        if name != "uvicorn.access":
            continue
        if not any(isinstance(item, HealthAccessFilter) for item in logger.filters):
            logger.addFilter(HealthAccessFilter())
