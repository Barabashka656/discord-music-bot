import os
import logging
from logging import handlers

from bot.data.config import LOGS_FOLDER


def configure_logger():
# Create a logger
    logging.basicConfig(level=logging.DEBUG)
    # Create a folder for log files
    log_folder = LOGS_FOLDER
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    # Create a rotating file handler
    log_file = os.path.join(log_folder, 'log.log')
    handler = handlers.RotatingFileHandler(log_file, maxBytes=1e7, backupCount=5)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    # Add the handler to the root logger
    logging.getLogger().addHandler(handler)
