import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "event": "",
        }
        # If record.msg is a dict, merge
        if isinstance(record.msg, dict):
            log_record.update(record.msg)
        else:
            log_record["event"] = str(record.msg)
        return json.dumps(log_record)

# Remove old handlers
for h in logging.root.handlers[:]:
    logging.root.removeHandler(h)

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    filemode="a",
    format="%(message)s"
)

root_logger = logging.getLogger()
for handler in root_logger.handlers:
    handler.setFormatter(JsonFormatter())

# Suppress uvicorn, FastAPI, etc. from writing to app.log
for name in ["uvicorn", "uvicorn.access", "fastapi"]:
    logging.getLogger(name).propagate = False
    logging.getLogger(name).handlers = []
