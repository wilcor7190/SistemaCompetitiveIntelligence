"""Logger with rich console output."""

import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

console = Console()

_logger: logging.Logger | None = None


def setup_logger(
    level: str = "INFO",
    log_to_file: bool = True,
    file_path: str = "logs/scraping.log",
) -> logging.Logger:
    """Configure and return the application logger."""
    global _logger

    log_level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger("ci_scraper")
    logger.setLevel(log_level)
    logger.handlers.clear()

    # Rich console handler
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    rich_handler.setLevel(log_level)
    logger.addHandler(rich_handler)

    # File handler
    if log_to_file:
        log_file = Path(file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """Get the application logger, creating it with defaults if needed."""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger
