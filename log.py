from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import structlog
import sys

DEFAULT_LOG_ROOT_DIRECTORY = "~/Library/Logs/"

# Based on code from @dhruvshirar on medium.com, with thanks
# https://medium.com/@dhruvshirar/structured-logging-in-python-a-practical-guide-for-production-systems-9659f461fa93
# 
def start_logging(
      log_level: str = "INFO", 
      log_root_dir: Path | str = DEFAULT_LOG_ROOT_DIRECTORY,
      app: str = "app",
      copy_to_stdout: bool = False,
    ) -> None:
    """ Set up structured logging """

    # Create log directory
    log_root_dir = Path(log_root_dir) # Ensure we are working with a Path object
    log_dir = log_root_dir.expanduser() / app
    log_dir.mkdir(parents=True, exist_ok=True)

    # Timestamped log filename - sorts chronologically
    log_file_name = Path(f"{app}_{datetime.now().strftime('%Y-%m-%d___%H-%M-%S')}.log")
    log_file = log_dir / log_file_name

    # File handler: 10MB max per file, keep 5 backups = 60MB total max
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter('%(message)s'))

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    # Remove existing handlers to avoid duplicates if called more than once
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(file_handler)

    # Add console handler, if required
    if copy_to_stdout:
      stream_handler = logging.StreamHandler(sys.stdout)
      stream_handler.setFormatter(logging.Formatter('%(message)s'))
      root_logger.addHandler(stream_handler)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )