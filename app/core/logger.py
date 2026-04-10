"""
app/core/logger.py
Structured logging using loguru.
All application modules import `logger` from here.
"""

import sys
from loguru import logger
from app.core.config import settings

# Remove default handler, add our own
logger.remove()
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
        "<level>{message}</level>"
    ),
    colorize=True,
)

# Also write to file
logger.add(
    "logs/app.log",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    format="{time} | {level} | {name}:{function} - {message}",
)
