from bot.data.config import LAVALINK_PASSWORD

import mafic
import discord
from discord.ext import commands


class MyBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._activity = set_status_activity()
        self.pool = mafic.NodePool(self)
        self.loop.create_task(self.add_nodes())

    async def add_nodes(self):
        await self.pool.create_node(
            host="localhost",
            port=2333,
            label="SASASA2",
            password=LAVALINK_PASSWORD,
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Im logged in as {self.user}")
        print(f'Bot is ready!{self.is_ready()}')
        print(f"In {len(self.guilds)} guilds")
        print("-----------------------------")
