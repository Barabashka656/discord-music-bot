# from bot.utils.status_activity_funcs import (
#    set_status_activity
# )
from bot.data.config import LAVALINK_PASSWORD
import disnake
from disnake.ext import (
    commands,
    tasks
)
import mafic


class MyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._activity = set_status_activity()
        self.pool = mafic.NodePool(self)
        self.loop.create_task(self.add_nodes())

    async def add_nodes(self):
        await self.pool.create_node(
            host="localhost",  # localhost
            port=2333,
            label="SASASA",
            password=LAVALINK_PASSWORD,
        )

    # @tasks.loop(hours=1)
    # async def set_status_task(self):
    #
    #    new_status_activity = set_status_activity(self._activity)
#
    #    print(new_status_activity)
    #    await self.change_presence(activity=disnake.Activity(
    #            type=disnake.ActivityType.playing,
    #            name=new_status_activity
    #        ))
    #    self._activity = new_status_activity

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Im logged in as {self.user}")
        print(f'Bot is ready!{self.is_ready()}')
        print(f"In {len(self.guilds)} guilds")
        print("-----------------------------")
        # self.set_status_task.start()
        await self.change_presence(activity=disnake.Activity(
            type=disnake.ActivityType.unknown
        ))
