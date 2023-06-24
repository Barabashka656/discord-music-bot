import os

from bot.data.loader import bot


def load_cogs(ROOT_DIR: str):
    bot_dir = 'bot'
    cogs_dir = 'cogs'
    cogs_foulder = os.path.join(bot_dir, cogs_dir)
    root_cogs_foulder = os.path.join(ROOT_DIR, cogs_foulder)

    for name in os.listdir(root_cogs_foulder):
        if name.endswith(".py") and os.path.isfile(os.path.join(cogs_foulder, name)):
            bot.load_extension(f"{bot_dir}.{cogs_dir}.{name[:-3]}")
