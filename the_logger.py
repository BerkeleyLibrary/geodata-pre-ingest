import logging
import os
from logging.handlers import RotatingFileHandler

# Called at the time when select data process path
def setup_logger(log_dir, log_name="process.log"):        
    log_file = os.path.join(log_dir, log_name)
    logger = logging.getLogger("GeoblacklightLogger")
    logger.setLevel(logging.INFO)

    # Use rotating file handler to avoid locking issues
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger