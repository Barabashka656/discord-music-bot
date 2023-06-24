import os

from dotenv import (
    load_dotenv,
    find_dotenv
)


load_dotenv(find_dotenv())
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD')
