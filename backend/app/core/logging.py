import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Any

from app.core.config import Settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "event": "",
            "logger": record.name,
            "module": record.module,
        }
        if isinstance(record.msg, dict):
            payload.update(record.msg)
        else:
            payload["event"] = record.getMessage()
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(settings: Settings) -> None:
    settings.ensure_storage()
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    for handler in root.handlers[:]:
        root.removeHandler(handler)

    file_handler = RotatingFileHandler(
        settings.app_log_path,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(JsonFormatter())
    root.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())
    root.addHandler(console_handler)

    for name in ["uvicorn", "uvicorn.access", "fastapi"]:
        logging.getLogger(name).propagate = False
