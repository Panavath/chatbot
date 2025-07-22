import logging
import sys
from pathlib import Path
from datetime import datetime

from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def get_status_color(status_code: int) -> str:
    if status_code >= 500:
        return "<red>"
    elif status_code >= 400:
        return "<yellow>"
    elif status_code >= 300:
        return "<cyan>"
    elif status_code >= 200:
        return "<green>"
    else:
        return "<white>"

def color_status_code(status_code: int) -> str:
    color = get_status_color(status_code)
    return f"{color}{status_code}</>"

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.root.handlers = []

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.remove()
    logger.add(sys.stdout, format=log_format, colorize=True, diagnose=False, catch=True)
    logger.add(
        log_dir / "app-{time:DD-MM-YY}.log",
        format=log_format,
        rotation="00:00",
        retention="30 days",
        compression="zip",
        level="DEBUG",
        catch=True
    )

    logger.level("ERROR", color="<red>")
    logger.level("WARNING", color="<yellow>")
    logger.level("INFO", color="<green>")

    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(InterceptHandler())

    for name in logging.root.manager.loggerDict.keys():
        if name.startswith("uvicorn."):
            logging.getLogger(name).handlers = []

    return logger

logger = setup_logging()