import os

from dotenv import (
    load_dotenv,
    find_dotenv
)


load_dotenv(find_dotenv())
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILDS = int(os.getenv('GUILDS'))
INFO_CHANNEL = int(os.getenv('INFO_CHANNEL'))
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD')
JAVA_PATH = os.getenv('JAVA_PATH')
FOLDER = os.getenv('FOLDER')
SUPPORTED_LINKS_PATH = os.getenv('SUPPORTED_LINKS_PATH')
