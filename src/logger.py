from __future__ import annotations

import logging
from datetime import date
from pathlib import Path


def setup_logger(logs_dir: Path = Path("logs"), name: str = "bot_teleoftamo") -> logging.Logger:
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"{date.today().isoformat()}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
