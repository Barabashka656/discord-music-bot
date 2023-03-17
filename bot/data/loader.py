from bot.utils.bot_class import MyBot

import disnake


bot = MyBot(
    command_prefix="?",
    help_command=None,
    intents=disnake.Intents.all()
)

