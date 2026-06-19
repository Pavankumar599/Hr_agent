# hr_agent/logger.py

import logging
import os
from datetime import datetime

def setup_logger():
    # Create a logs/ folder if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Log file named with today's date → logs/hr_agent_2024-01-15.log
    log_filename = f"logs/hr_agent_{datetime.now().strftime('%Y-%m-%d')}.log"

    # Configure the logger
    logging.basicConfig(
        level=logging.INFO,                  # minimum level to record
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_filename),   # write to file
            logging.StreamHandler()              # also print to console/HF logs
        ]
    )

    logger = logging.getLogger("hr_agent")
    logger.info("Logger initialized")
    return logger

# Create one global logger instance
logger = setup_logger()