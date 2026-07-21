import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Import output directory configuration
try:
    from config import OUTPUT_DIR
except ImportError:
    # Fallback to a default directory if imported outside the workspace context
    OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

# Ensure the output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE_PATH = OUTPUT_DIR / "medical_analyzer.log"

def setup_logger(name: str = "medical_analyzer", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up and returns a logger instance with dual output sinks:
    1. Console (sys.stdout)
    2. Rotating File (outputs/medical_analyzer.log)
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if the logger has already been initialized
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)
    
    # Logging format: timestamp - source_name - level - message
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # 2. Rotating File Handler (Max 5MB per file, keeping up to 3 backups)
    try:
        file_handler = RotatingFileHandler(
            filename=LOG_FILE_PATH,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback to printing error if log file cannot be created
        print(f"Warning: Failed to initialize file logger at {LOG_FILE_PATH} due to: {e}", file=sys.stderr)

    return logger

# Create a default package-level logger
logger = setup_logger()
