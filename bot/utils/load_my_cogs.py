import os

from bot.data.config import COGS_FOLDER
from bot.data.loader import bot


def load_cogs():
    for name in os.listdir(COGS_FOLDER):
        if name.endswith(".py") and os.path.isfile(f"{COGS_FOLDER}/{name}"):
            bot.load_extension(f"bot.cogs.{name[:-3]}")
