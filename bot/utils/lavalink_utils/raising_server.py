import os

def start_server():
    current_dir = os.getcwd()
    java_path = os.path.join('bot', 'utils', 'lavalink_utils')
    os.chdir(java_path)
    os.system('start java -jar Lavalink.jar')
    os.chdir(current_dir)
