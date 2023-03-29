import os

from dotenv import (
    load_dotenv,
    find_dotenv
)


load_dotenv(find_dotenv())
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD')
JAVA_PATH = os.getenv('JAVA_PATH')
COGS_FOLDER = os.getenv('COGS_FOLDER')
LOGS_FOLDER = os.getenv('LOGS_FOLDER')
SUPPORTED_LINKS_PATH = os.getenv('SUPPORTED_LINKS_PATH')
FFMPEG_EXE = os.getenv('FFMPEG_EXE')

