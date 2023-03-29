import logging
from logging.handlers import RotatingFileHandler
import os
import time

from bot.data.config import (
    DISCORD_TOKEN,
    JAVA_PATH,
    COGS_FOLDER,
    LOGS_FOLDER
)
from bot.data.loader import bot


if __name__ == "__main__":
    os.makedirs(os.path.dirname(LOGS_FOLDER), exist_ok=True)
    log_name = f"{LOGS_FOLDER}.log"
    logger = logging.getLogger('discord')
    filesize = 1024 * 1024 * 1024
    handler = logging.FileHandler(filename=log_name, encoding='utf-8', mode='w')
    handler = RotatingFileHandler(log_name, maxBytes=filesize, backupCount=30)
    logger.addHandler(handler)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    current_dir = os.getcwd()
    os.chdir(JAVA_PATH)
    os.system('start java -jar Lavalink.jar')
    time.sleep(10)
    os.chdir(current_dir)

    for name in os.listdir(COGS_FOLDER):
        if name.endswith(".py") and os.path.isfile(f"{COGS_FOLDER}/{name}"):
            bot.load_extension(f"bot.cogs.{name[:-3]}")
    bot.run(DISCORD_TOKEN)
    