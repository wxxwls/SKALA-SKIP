"""Logging configuration using loguru."""
import sys
from loguru import logger

from app.config.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    logger.add(
        "logs/app.log",
        format=log_format,
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )


def get_logger(name: str = __name__):
    """Get a logger instance with the given name."""
    return logger.bind(name=name)
