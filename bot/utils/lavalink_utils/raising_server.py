import os

from bot.data.config import JAVA_PATH


def start_server():
    current_dir = os.getcwd()
    os.chdir(JAVA_PATH)
    os.system('start java -jar Lavalink.jar')
    os.chdir(current_dir)
