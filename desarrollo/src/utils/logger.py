"""Logger with rich console output and per-run file logging."""

import logging
import time
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

console = Console()

_logger: logging.Logger | None = None
_current_log_file: str | None = None


def setup_logger(
    level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs",
    run_id: str | None = None,
) -> logging.Logger:
    """Configure and return the application logger.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        log_to_file: Whether to also log to a file.
        log_dir: Directory for log files.
        run_id: Optional run ID to include in the log filename.
    """
    global _logger, _current_log_file

    log_level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger("ci_scraper")
    logger.setLevel(log_level)
    logger.handlers.clear()

    # Rich console handler — pretty colored output for humans
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    rich_handler.setLevel(log_level)
    logger.addHandler(rich_handler)

    # File handler — full traceability for post-mortem analysis
    if log_to_file:
        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)

        # Per-run filename: scraping_YYYYMMDD_HHMMSS_<runid>.log
        ts = time.strftime("%Y%m%d_%H%M%S")
        suffix = f"_{run_id}" if run_id else ""
        log_file = log_dir_path / f"scraping_{ts}{suffix}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # File always captures DEBUG

        file_formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)-7s] [%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        _current_log_file = str(log_file)
        logger.info(f"[logger] File log: {log_file}")

    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """Get the application logger, creating it with defaults if needed."""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


def get_current_log_file() -> str | None:
    """Return path to the current log file (if any)."""
    return _current_log_file
