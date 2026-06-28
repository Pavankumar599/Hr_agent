# hr_agent/logger.py

import logging
import sys
import os
from datetime import datetime

def setup_logger():
    handlers = [
        logging.StreamHandler(sys.stdout)  # always works — HF + local
    ]

    # only write to file if running locally (HF sets SPACE_ID env variable)
    if not os.getenv("SPACE_ID"):
        os.makedirs("logs", exist_ok=True)
        log_filename = f"logs/hr_agent_{datetime.now().strftime('%Y-%m-%d')}.log"
        handlers.append(logging.FileHandler(log_filename))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers
    )

    logger = logging.getLogger("hr_agent")
    logger.info("Logger initialized")
    return logger

logger = setup_logger()