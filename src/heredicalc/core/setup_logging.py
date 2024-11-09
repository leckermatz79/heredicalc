# core/setup_logging.py
import logging
import sys

def setup_logging(log_level="INFO", log_file=None):
    """Configures logging with specified log level and optional log file.
    
    Args:
        log_level (str): The logging level as a string (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        log_file (str): Optional file path for logging output to a file.
    """
    # Convert log level string to logging level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(level)

    # Handler for stdout (DEBUG and INFO levels)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)  # Set to DEBUG to capture all messages up to INFO
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    stdout_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Handler for stderr (WARNING and above)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Clear any existing handlers, then add the new ones
    logger.handlers = []  # Ensures no duplicate handlers
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)