# shared/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler

from shared.config import Config

# Simple colored output
CSI = "\x1B["
RESET = CSI + "0m"
LEVEL_COLORS = {
    'DEBUG': CSI + '36m',   # Cyan
    'INFO': CSI + '32m',    # Green
    'WARNING': CSI + '33m', # Yellow
    'ERROR': CSI + '31m',   # Red
    'CRITICAL': CSI + '41m', # Red bg
}

_logger = None

def get_logger(name: str = __name__) -> logging.Logger:
    global _logger
    if _logger:
        return _logger

    _logger = logging.getLogger(name)
    _logger.setLevel(Config.LOG_LEVEL)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(Config.LOG_LEVEL)

    # Color formatter
    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            levelname = record.levelname
            color = LEVEL_COLORS.get(levelname, RESET)
            record.levelname = f"{color}{levelname}{RESET}"
            return super().format(record)

    fmt = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    ch.setFormatter(fmt)
    _logger.addHandler(ch)

    # File handler
    fh = RotatingFileHandler("calvinos.log", maxBytes=5*1024*1024, backupCount=3)
    fh.setLevel(Config.LOG_LEVEL)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    _logger.addHandler(fh)

    return _logger