# src/logger.py

import logging
import os

def get_logger(
    name="educational_rag",
    log_dir="outputs/logs",
    level=logging.INFO,
    console: bool = True,
    file: bool = True,
):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{name}.log")

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Remove any existing handlers to avoid duplicate logs in Jupyter/interactive runs
    if logger.hasHandlers():
        logger.handlers.clear()

    if console:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logger.addHandler(ch)
    if file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(fh)

    return logger
