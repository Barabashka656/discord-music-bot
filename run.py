import os
import time

from bot.data.loader import bot
from bot.data.config import (
    DISCORD_TOKEN,
    JAVA_PATH,
    FOLDER
)


if __name__ == "__main__":
    current_dir = os.getcwd()
    os.chdir(JAVA_PATH)
    os.system('start java -jar Lavalink.jar')

    time.sleep(10)
    os.chdir(current_dir)
    for name in os.listdir(FOLDER):
        if name.endswith(".py") and os.path.isfile(f"bot/cogs/{name}"):
            bot.load_extension(f"bot.cogs.{name[:-3]}")

    bot.run(DISCORD_TOKEN)
