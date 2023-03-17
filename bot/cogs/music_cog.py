import collections
import json

from bot.data.config import (
    INFO_CHANNEL,
    SUPPORTED_LINKS_PATH
)

import mafic
import disnake
from disnake.ext import (
    commands,
)


class MusicCog(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.voice # TODO(LOL) : kek
        self.info_channel = INFO_CHANNEL
        self.queue: collections.deque = collections.deque()
        self.bot.loop.create_task(self.connect_nodes())

        with open(SUPPORTED_LINKS_PATH, 'r') as file:
            data: dict = json.load(file)

            self.SUPPORTED_LINKDS: dict = data

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

    @commands.slash_command()
    async def play(self, inter: disnake.ApplicationCommandInteraction, *, search: str):
        """
        play a song in your channel     
        """

        bot_voice_client = inter.guild.voice_client
        if not inter.user.voice:
            text = f"{inter.user.mention}, buddy,\ngo to the voice channel"
            return await inter.send(content=text, ephemeral=True)

        voice_channel = inter.user.voice.channel

        if not bot_voice_client:

            player = await voice_channel.connect(cls=mafic.Player, reconnect=True)
            await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        else:

            if voice_channel.id != bot_voice_client.channel.id:
                text = f"{inter.user.mention}, bot isn't connected to the channel"
                return await inter.send(content=text, ephemeral=True)

            player = bot_voice_client

        if search.startswith(self.SUPPORTED_LINKDS.get("spotify").get("start_with")):
            try:
                tracks = await player.fetch_tracks(search, mafic.SearchType.SPOTIFY_SEARCH)
            except mafic.TrackLoadException as e:

                text = f"{inter.user.mention},\nInvalid spotify link"
                return await inter.send(content=text, ephemeral=True)

        elif search.startswith(self.SUPPORTED_LINKDS.get("deezer").get("start_with")[0]) or\
                search.startswith(self.SUPPORTED_LINKDS.get("deezer").get("start_with")[1]):
            try:
                tracks = await player.fetch_tracks(search, mafic.SearchType.DEEZER_SEARCH)
            except mafic.TrackLoadException as e:

                text = f"{inter.user.mention},\nInvalid deezer link"
                return await inter.send(content=text, ephemeral=True)

        elif search.startswith(self.SUPPORTED_LINKDS.get("yandex_music").get("start_with")):
            try:
                tracks = await player.fetch_tracks(search, mafic.SearchType.DEEZER_SEARCH)
            except mafic.TrackLoadException as e:

                text = f"{inter.user.mention},\nInvalid Yandex Music link"
                return await inter.send(content=text, ephemeral=True)

        else:
            try:
                tracks = await player.fetch_tracks(search)
            except mafic.TrackLoadException as e:

                text = f"{inter.user.mention},\nInvalid youtube link\n"
                return await inter.send(content=text, ephemeral=True)

        if not tracks:
            return await inter.send("I won't play this", ephemeral=True)

        x = 0
        if isinstance(tracks, mafic.Playlist):
            for track in tracks.tracks:
                self.queue.append(track)
            x = 1
            if search.startswith("https://open.spotify.com/album"):
                await inter.send(f"Added {tracks.name} album")
            else:
                await inter.send(f"Added {tracks.name}.")
        else:
            track = tracks[0]

            self.queue.append(track)

        if len(self.queue) == 1:
            try:
                await player.play(track)
            except mafic.PlayerNotConnected as ex:
                await player.disconnect()

                player = await voice_channel.connect(cls=mafic.Player, reconnect=True)
                await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)

            return await inter.send(f"Playing {track.title}.")

        if x == 0:
            await inter.send(f"Added {track.title}.")
        else:
            try:
                await player.play(track)
            except mafic.PlayerNotConnected as ex:
                await player.disconnect()

                player = await voice_channel.connect(cls=mafic.Player, reconnect=True)
                await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)

    @commands.slash_command()
    async def skip(self, inter: disnake.ApplicationCommandInteraction):
        """
        skip that song
        """
        bot_voice_client = inter.guild.voice_client

        if not inter.user.voice:
            text = f"{inter.user.mention}, buddy,\ngo to the voice channel"
            return await inter.send(content=text, ephemeral=True)

        voice_channel = inter.user.voice.channel

        if not bot_voice_client or len(self.queue) == 0:
            return await inter.send("Скипать нечего", ephemeral=True)

        if voice_channel.id != bot_voice_client.channel.id:
            text = text = f"{inter.user.mention}, bot isn't connected to the channel"
            return await inter.send(content=text, ephemeral=True)

        player: mafic.Player = bot_voice_client

        previous_track: mafic.Track = self.queue[0]
        await player.stop()

        if len(self.queue) > 0:
            text = f"Track: {previous_track.title} was skipped,\nNow playing: {player.current.title}"
        else:
            text = f"Track: {previous_track.title} was skipped"
        await inter.send(content=text, ephemeral=True)

    @commands.slash_command()
    async def current(self, inter: disnake.ApplicationCommandInteraction):
        bot_voice_client = inter.guild.voice_client

        if not bot_voice_client:
            text = f"{inter.user.mention}, bot isn't connected to the channel"
            return await inter.send(content=text, ephemeral=True)

        if not inter.user.voice:
            text = f"{inter.user.mention}, buddy,\ngo to the voice channel"
            return await inter.send(content=text, ephemeral=True)

        tracks_in_queue = len(self.queue)
        if tracks_in_queue == 0:
            text = "Nothing is playing right now"
        elif tracks_in_queue == 1:
            text = f"Now playing {self.queue[0]}"
        else:
            text = f"Now playing {self.queue[0]}, and {tracks_in_queue-1} tracks"
        await inter.send(content=text, ephemeral=True)

    @commands.slash_command()
    async def pause(self, inter: disnake.ApplicationCommandInteraction):
        """
        pause current song 
        """

        bot_voice_client = inter.guild.voice_client
        if not inter.user.voice:
            text = f"{inter.user.mention}, buddy,\ngo to the voice channel"
            return await inter.send(content=text, ephemeral=True)

        if not bot_voice_client:
            text = f"{inter.user.mention}, bot isn't connected to the channel"
            return await inter.send(content=text, ephemeral=True)
        else:
            player = bot_voice_client

        await player.pause()

        await inter.send(f"paused", ephemeral=True)

    @commands.slash_command()
    async def resume(self, inter: disnake.ApplicationCommandInteraction):
        """
        resume current song
        """
        bot_voice_client = inter.guild.voice_client
        if not inter.user.voice:
            text = f"{inter.user.mention}, buddy,\ngo to the voice channel"
            return await inter.send(content=text, ephemeral=True)

        if not bot_voice_client:
            text = f"{inter.user.mention}, bot isn't connected to the channel"
            return await inter.send(content=text, ephemeral=True)
        else:
            player = bot_voice_client

        await player.resume()

        await inter.send(f"resumed", ephemeral=True)

    @commands.slash_command()
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        """
        clear the queue
        """

        bot_voice_client = inter.guild.voice_client
        if not inter.user.voice:
            text = f"{inter.user.mention}, buddy,\ngo to the voice channel"
            return await inter.send(content=text, ephemeral=True)

        voice_channel = inter.user.voice.channel

        if not bot_voice_client or len(self.queue) == 0:
            return await inter.send("there is nothing to skip", ephemeral=True)

        if voice_channel.id != bot_voice_client.channel.id:
            text = f"{inter.user.mention}, bot isn't connected to the channel"
            return await inter.send(content=text, ephemeral=True)

        player: mafic.Player = bot_voice_client

        self.queue.clear()
        await player.stop()

        await inter.send(f"stop", ephemeral=True)

    @commands.slash_command()
    async def disconnect(self, inter: disnake.ApplicationCommandInteraction):
        """
        disconnect bot from channel
        """

        bot_voice_client = inter.guild.voice_client
        if not inter.user.voice:
            text = f"{inter.user.mention}, buddy,\ngo to the voice channel"
            return await inter.send(content=text, ephemeral=True)

        voice_channel = inter.user.voice.channel

        if not bot_voice_client:
            player = await voice_channel.connect(cls=mafic.Player)
            await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        else:
            player = bot_voice_client

        await player.disconnect()

        await inter.send(f"disconnect")

    @commands.Cog.listener()
    async def on_track_end(
            self,
            data: mafic.TrackEndEvent
    ):

        player: mafic.Player = data.player
        if len(self.queue) == 0:
            return

        self.queue.popleft()

        if len(self.queue) > 0:
            track = self.queue[0]
            try:
                await player.play(track)
            except mafic.PlayerNotConnected as ex:
                await player.disconnect()
                await player.connect(timeout=60, reconnect=True, self_deaf=True)
                await player.play(track)

    @commands.Cog.listener("on_voice_state_update")
    async def player_vc_disconnect(
            self,
            member: disnake.Member,
            before: disnake.VoiceState,
            after: disnake.VoiceState
    ):
        if not member.voice:
            self.queue.clear()
        # if before.channel == after.channel:
        #    return

        # if member.bot and member.id != self.bot.user.id:  # ignor other bots
        #    return
        #
        # if member.bot and member.id != self.bot.user.id:  # ignor other bots
        #    return


def setup(bot: commands.Bot):
    bot.add_cog(MusicCog(bot))
    print(f"> Extension {__name__} is ready")
