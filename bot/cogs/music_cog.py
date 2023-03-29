import json

from collections import (
    namedtuple,
    deque
)
from bot.data.config import (
    SUPPORTED_LINKS_PATH,
    FFMPEG_EXE
)

import mafic
import humanize
import time
import discord
from discord import FFmpegPCMAudio
from discord.ext import (
    commands,
)


class MusicCog(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.RadioTrack = namedtuple('RTrack', 'title url')
        self.queue: deque[mafic.Track | self.RadioTrack] = deque()
        self.bot.loop.create_task(self.connect_nodes())
        UrlDict = namedtuple('UrlDict', 'SPOTIFY_THUMBNAIL YOUTUBE_THUMBNAIL GACHI_RADIO GACHI_THUMBNAIL RADIO_THUMBNAIL')
        self.url_tuple: UrlDict = UrlDict(
            'https://cdn.discordapp.com/attachments/1072997060225278032/1090332924987047947/Spotify_Icon.png',
            'https://cdn.discordapp.com/attachments/1072997060225278032/1090333233088041040/youtube_icon.png',
            'https://stream-017.zeno.fm/f174214qvzzuv?zs=8Btpgg72Tg-uHINApotdaw&aw_0_req_lsid=346f2b546c923317c8f8b8cb04ad8743',
            'https://cdn.discordapp.com/attachments/1072997060225278032/1090354097338720327/gachi.png',
            'https://cdn.discordapp.com/attachments/1072997060225278032/1090355279398437004/radio.png'
        )

        with open(SUPPORTED_LINKS_PATH, 'r') as file:
            data: dict = json.load(file)

            self.SUPPORTED_LINKDS: dict = data

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

    async def mafic_reconnect(
            self,
            inter: discord.ApplicationContext,
            track: mafic.Track,
            player: mafic.Player
        ):
        print('reconnect')
        voice_channel: discord.VoiceChannel = inter.user.voice.channel
        await player.disconnect()
        player = await voice_channel.connect(cls=mafic.Player, reconnect=True)
        await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        await player.play(track)
        embed = self.create_track_embed(inter)
        await inter.send_response(embed=embed)
        
        
    def humanize_track_length(self) -> str:
        track = self.queue[0]
        
        seconds = int(track.length / 1000)
    
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        track_length = f"{m:02d}:{s:02d}"
        if h > 0:
            track_length = f"{h:d}" + track_length
        return track_length

    def create_radio_track_embed(
            self,
            inter: discord.ApplicationContext
        ) -> discord.Embed:

        track = self.queue[0]

        embed = discord.Embed(color=inter.guild.me.color)
        
        
        
            
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.url_tuple.RADIO_THUMBNAIL,
        )
        embed.description = f'Playing "**{track.title}**" \n{track.url}'
        embed.add_field(name="Station", value='Gachi Station')

        thumbnail_url = self.url_tuple.GACHI_THUMBNAIL
        embed.set_thumbnail(url=thumbnail_url)
        
        return embed


    def create_track_embed(
            self,
            inter: discord.ApplicationContext
        ) -> discord.Embed:
         
        track = self.queue[0]

        track_length = self.humanize_track_length()

        embed = discord.Embed(color=inter.guild.me.color)
        
        if track.source == 'youtube':
            icon_url = self.url_tuple.YOUTUBE_THUMBNAIL
            thumbnail_url = f"https://i.ytimg.com/vi/{track.identifier}/hq720.jpg"
           
            embed.set_thumbnail(url=thumbnail_url)
        elif track.source == 'spotify':
            icon_url = self.url_tuple.SPOTIFY_THUMBNAIL
            
        embed.set_author(
            name=self.bot.user.name,
            icon_url=icon_url,
        )
        embed.description = f'Playing "**{track.title}**" \n{track.uri}'
        embed.add_field(name="Artist", value=track.author, inline=True)
        embed.add_field(name="song length", value=track_length, inline=True)
        embed.add_field(
            name="In queue", 
            value=str(len(self.queue)-1) + ' tracks', 
            inline=True)
        
        return embed
      
    
    async def is_radio_now(
        self,
        inter: discord.ApplicationContext
    ):

        if isinstance(self.queue[0], tuple):
            text = f"{inter.user.mention}, now playing radio({self.queue[0].title})\n" + \
                "turn it off to listen to other songs"
            await inter.send_response(content=text, ephemeral=True)
            return True
        return False

    async def is_user_in_voice_channel(
        self,
        inter: discord.ApplicationContext
    ):
        if not inter.user.voice:
            text = f"{inter.user.mention}, buddy,\ngo to the voice channel"
            await inter.send_response(content=text, ephemeral=True)
            return False
        return True

    async def is_bot_in_voice_channel(
        self,
        inter: discord.ApplicationContext
    ):
        voice_channel = inter.user.voice.channel
        bot_voice_client = inter.guild.voice_client

        if not bot_voice_client or voice_channel.id != bot_voice_client.channel.id:
            text = f"{inter.user.mention}, bot isn't connected to the channel"
            await inter.send_response(content=text, ephemeral=True)
            return None
        return True

    async def mafic_connect(
        self,
        inter: discord.ApplicationContext,
    ):
        voice_channel = inter.user.voice.channel
        bot_voice_client = inter.guild.voice_client

        if not bot_voice_client:
            player: mafic.Player = await voice_channel.connect(cls=mafic.Player, reconnect=True)
            await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        else:
            if not await self.is_bot_in_voice_channel(inter):
                return None

            if isinstance(bot_voice_client, discord.VoiceClient):
                player = bot_voice_client

                await player.disconnect()
                player: mafic.Player = await voice_channel.connect(cls=mafic.Player, reconnect=True)
                await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)
            else:
                player: mafic.Player = bot_voice_client

        return player

    async def get_mafic_player(
        self,
        inter: discord.ApplicationContext
    ):

        if not await self.is_user_in_voice_channel(inter):
            return None

        if len(self.queue) > 0 and await self.is_radio_now(inter):
            return None

        return await self.mafic_connect(inter)

    async def voice_connect(
        self,
        inter: discord.ApplicationContext,
    ):
        voice_channel = inter.user.voice.channel
        bot_voice_client = inter.guild.voice_client

        if not bot_voice_client:
            player = await voice_channel.connect(reconnect=True, timeout=60)
            await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)

        else:
            if not await self.is_bot_in_voice_channel(inter):
                return None

            if isinstance(bot_voice_client, mafic.Player):
                player = bot_voice_client
                await player.disconnect()
                player = await voice_channel.connect(reconnect=True, timeout=60)
                await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)
            else:
                player: discord.VoiceClient = bot_voice_client

        return player

    async def get_voice_client(
        self,
        inter: discord.ApplicationContext
    ):

        if not await self.is_user_in_voice_channel(inter):
            return None

        return await self.voice_connect(inter)

    async def add_song_to_queue(
        self,
        inter: discord.ApplicationContext,
        player: mafic.Player | discord.VoiceClient,
        tracks: mafic.Playlist | list[mafic.Track],
        search: str
    ):
        voice_channel: discord.VoiceChannel = inter.user.voice.channel
        if not inter.guild.voice_client:
            player = await voice_channel.connect(cls=mafic.Player, reconnect=True, timeout=60)
            await inter.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        
        is_queue_empty = False

        if len(self.queue) == 0:
            is_queue_empty = True
        if isinstance(tracks, mafic.Playlist):
            self.add_playlist_in_queue(tracks)
            is_playlist = True
        else:
            self.add_track_in_queue(tracks)
            is_playlist = False
        track: mafic.Track = self.queue[0]
        
        if len(self.queue) == 1:        # nothing plays and one track added
            try:

                await player.play(track)
                embed = self.create_track_embed(inter)
                await inter.send_response(embed=embed)
            except mafic.PlayerNotConnected as e:
                await self.mafic_reconnect(inter, track, player)
                embed = self.create_track_embed(inter)
                await inter.send_response(embed=embed)
            return
            

        if not is_playlist:     # something plays and one track added
            await inter.send_response(f"Added {tracks[0].title}.")
        else:
            try:
                if is_queue_empty:      # nothing plays and some tracks added
                    await player.play(track)
                    embed = self.create_track_embed(inter)
                await inter.send_response(embed=embed)
                if search.startswith("https://open.spotify.com/album"):
                    await inter.send_response(f"Added {tracks.name} (spotify album)")
                else: 
                    await inter.send_response(f"Added {tracks.name}.")

            except mafic.PlayerNotConnected as e:
                self.mafic_reconnect(inter, track, player)

    def add_playlist_in_queue(
        self,
        tracks: mafic.Playlist
    ):
        for track in tracks.tracks:
            self.queue.append(track)

        

    def add_track_in_queue(
        self,
        tracks: list[mafic.Track],
    ):

        track = tracks[0]
        self.queue.append(track)

    async def fetch_mafic_tracks(
        self,
        inter: discord.ApplicationContext,
        search: str,
        player: mafic.Player
    ):
        if search.startswith(self.SUPPORTED_LINKDS.get("spotify").get("start_with")):
            try:
                tracks = await player.fetch_tracks(search, mafic.SearchType.SPOTIFY_SEARCH)
            except mafic.TrackLoadException:
                text = f"{inter.user.mention},\nInvalid spotify link"
                await inter.send_response(content=text, ephemeral=True)
                return None

        elif search.startswith(self.SUPPORTED_LINKDS.get("deezer").get("start_with")[0]) or\
                search.startswith(self.SUPPORTED_LINKDS.get("deezer").get("start_with")[1]):
            try:
                tracks = await player.fetch_tracks(search, mafic.SearchType.DEEZER_SEARCH)
            except mafic.TrackLoadException:
                text = f"{inter.user.mention},\nInvalid deezer link"
                await inter.send_response(content=text, ephemeral=True)
                return None

        elif search.startswith(self.SUPPORTED_LINKDS.get("yandex_music").get("start_with")):
            try:
                tracks = await player.fetch_tracks(search, mafic.SearchType.DEEZER_SEARCH)
            except mafic.TrackLoadException:
                text = f"{inter.user.mention},\nInvalid Yandex Music link"
                await inter.send_response(content=text, ephemeral=True)
                return None

        else:
            try:
                tracks = await player.fetch_tracks(query=search)
            except mafic.TrackLoadException:
                text = f"{inter.user.mention},\nInvalid youtube link\n"
                await inter.send_response(content=text, ephemeral=True)
                return None
        
        if not tracks:
            text = "I won't play this" 
            await inter.send_response(content=text, ephemeral=True)
            return None
        
        return tracks

    @commands.slash_command()
    async def radio(self, inter: discord.ApplicationContext):
        station = "Gachi Station"
        if len(self.queue) > 0:
            text = f"{inter.user.mention}, the radio can't be turned on\nwhen there are no songs in the queue\n"
            return await inter.send_response(content=text, ephemeral=True)
      
        player: discord.VoiceClient = await self.get_voice_client(inter)
       
        if not player:
            return
        
        player.play(FFmpegPCMAudio(executable=FFMPEG_EXE, source=self.url_tuple.GACHI_RADIO))
     
        
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=station
        ))

        self.queue.append(self.RadioTrack(station, self.url_tuple.GACHI_RADIO))
        embed = self.create_radio_track_embed(inter)
        await inter.send_response(embed=embed)
       

    @commands.slash_command()
    async def play(self, inter: discord.ApplicationContext, *, search: str):
        """
        play a song in your channel     
        """
        

        player: mafic.Player = await self.get_mafic_player(inter)
        if not player:
            return
        
        tracks = await self.fetch_mafic_tracks(inter, search, player)
        if not tracks:
            return

        
        await self.add_song_to_queue(
            inter=inter,
            player=player,
            tracks=tracks,
            search=search
        )
        

    @commands.slash_command()
    async def skip(self, inter: discord.ApplicationContext):
        """
        skip that song
        """
        if not await self.is_user_in_voice_channel(inter):
            return

        bot_voice_client = inter.guild.voice_client

        if not bot_voice_client or len(self.queue) == 0:
            return await inter.send_response("there is nothing to skip", ephemeral=True)

        if not await self.is_bot_in_voice_channel(inter):
            return

        player: mafic.Player | discord.VoiceClient = bot_voice_client

        if isinstance(self.queue[0], tuple):
            previous_track: str = self.queue[0]
            self.queue.clear()
            await player.disconnect()
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.unknown
            ))
        else:
            previous_track: str = self.queue[0]
            await player.stop()
        
        if len(self.queue) > 0:
            embed = self.create_track_embed(inter)
            if isinstance(self.queue[0], tuple):
                text = f"Track: {previous_track.title} was skipped,\nNow playing: {self.queue[0].title}"
            else:
                text = f"Track: {previous_track.title} was skipped,\nNow playing: {self.queue[0].title}"
        else:
            text = f"Track: {previous_track.title} was skipped,\nThe queue is empty"
            return await inter.send_response(content=text, ephemeral=True)  
          

        await inter.send_response(content=text, embed=embed, ephemeral=True)     
        

    @commands.slash_command()
    async def current(self, inter: discord.ApplicationContext):

        if not await self.is_bot_in_voice_channel(inter):
            return

        if not await self.is_user_in_voice_channel(inter):
            return

        if len(self.queue) == 0:
            text = "Nothing is playing right now"
            return await inter.send_response(content=text, ephemeral=True)
        
        if isinstance(self.queue[0], tuple):
            text = "Now playing radio station\n" + self.queue[0].title
            return await inter.send_response(content=text, ephemeral=True)

        embed = self.create_track_embed(inter)
       
        await inter.response.send_message(embed=embed)

    @commands.slash_command()
    async def pause(self, inter: discord.ApplicationContext):
        """
        pause current song 
        """

        if not await self.is_bot_in_voice_channel(inter):
            return

        if not await self.is_user_in_voice_channel(inter):
            return

        bot_voice_client = inter.guild.voice_client

        player: mafic.Track | discord.VoiceClient = bot_voice_client

        if isinstance(self.queue[0], tuple):
            player.pause()
        else:
            await player.pause()

        await inter.send_response(f"paused", ephemeral=True)

    @commands.slash_command()
    async def resume(self, inter: discord.ApplicationContext):
        """
        resume current song
        """
        if not await self.is_bot_in_voice_channel(inter):
            return

        if not await self.is_user_in_voice_channel(inter):
            return

        bot_voice_client = inter.guild.voice_client

        player: mafic.Track | discord.VoiceClient = bot_voice_client

        if isinstance(self.queue[0], tuple):
            player.resume()
        else:
            await player.resume()

        await inter.send_response(f"resumed", ephemeral=True)

    @commands.slash_command()
    async def clear(self, inter: discord.ApplicationContext):
        """
        clear the queue
        """
        bot_voice_client = inter.guild.voice_client
        if not await self.is_user_in_voice_channel(inter):
            return

        if not bot_voice_client or len(self.queue) == 0:
            return await inter.send_response("the queue is empty", ephemeral=True)

        if not await self.is_bot_in_voice_channel(inter):
            return
        tracks_count = len(self.queue)
        current_track = self.queue[0]

        self.queue.clear()
        self.queue.append(current_track)
        text = f"{tracks_count-1} tracks have been removed from the queue"
        await inter.send_response(content=text, ephemeral=True)
        

    @commands.slash_command()
    async def stop(self, inter: discord.ApplicationContext):
        """
        stop current song and clear the queue
        """

        bot_voice_client = inter.guild.voice_client
        if not await self.is_user_in_voice_channel(inter):
            return

        if not bot_voice_client or len(self.queue) == 0:
            return await inter.send_response("there is nothing to skip", ephemeral=True)

        if not await self.is_bot_in_voice_channel(inter):
            return

        player: mafic.Player | discord.VoiceClient = bot_voice_client
        tracks_count = len(self.queue)
        if isinstance(self.queue[0], tuple):
            self.queue.clear()
            await player.disconnect()
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.unknown
            ))
        else:
            self.queue.clear()
            await player.stop()
        text = f"{tracks_count} tracks have been removed from the queue"
        await inter.send_response(content=text, ephemeral=True)

    @commands.slash_command()
    async def disconnect(self, inter: discord.ApplicationContext):
        """
        disconnect bot from channel
        """

        if not await self.is_user_in_voice_channel(inter):
            return

        if not await self.is_bot_in_voice_channel(inter):
            return

        bot_voice_client = inter.guild.voice_client
        player = bot_voice_client

        await player.disconnect()
        await inter.send_response(f"disconnect")

    @commands.Cog.listener()
    async def on_track_start(
        self,
        data: mafic.TrackStartEvent
    ):
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=data.track.title
        ))

    @commands.Cog.listener()
    async def on_track_end(
        self,
        data: mafic.TrackEndEvent
    ):
        player: mafic.Player = data.player

        if len(self.queue) <= 1:
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.unknown
            ))
            self.queue.clear()
            return

        self.queue.popleft()

        if len(self.queue) > 0:
            track = self.queue[0]
            try:
                await player.play(track)
            except mafic.PlayerNotConnected as e:
                await player.disconnect()
                await player.connect(cls=mafic.Player, reconnect=True, self_deaf=True)
                await player.play(track)

    @commands.Cog.listener("on_voice_state_update")
    async def player_vc_disconnect(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        if not member.voice:
            self.queue.clear()
        # if before.channel == after.channel:
        #    return

        # if member.bot and member.id != self.bot.user.id:  # ignor other bots
        #    return

    @commands.slash_command()
    async def spotify(
        self,
        inter: discord.ApplicationContext,
        member: discord.Member
    ):
        """
        spotify song information of a user's spotify rich presence
        """
        activities = member.activities
        try:
            act = [
                activity
                for activity in activities
                if isinstance(activity, discord.Spotify)
            ][0]
        except IndexError:
            return await inter.response.send_message("No spotify was detected")
        start = humanize.naturaltime(discord.utils.utcnow() - act.created_at)
        
        name = act.title
        art = " ".join(act.artists)
        album = act.album
        duration = round(((act.end - act.start).total_seconds() / 60), 2)
        min_sec = time.strftime(
            "%M:%S", time.gmtime((act.end - act.start).total_seconds())
        )
        current = round(
            ((discord.utils.utcnow() - act.start).total_seconds() / 60), 2)
        min_sec_current = time.strftime(
            "%M:%S", time.gmtime(
                (discord.utils.utcnow() - act.start).total_seconds())
        )
        embed = discord.Embed(color=inter.guild.me.color)
        embed.set_author(
            name=member.display_name,
            icon_url="https://netsbar.com/wp-content/uploads/2018/10/Spotify_Icon.png",
        )
        embed.description = f'Listening To  "**{name}**" \n(https://open.spotify.com/track/{act.track_id})'
        embed.add_field(name="Artist", value=art, inline=True)
        embed.add_field(name="Album", value=album, inline=True)
        embed.set_thumbnail(url=act.album_cover_url)
        embed.add_field(name="Started Listening", value=start, inline=True)
        percent = int((current / duration) * 25)
        perbar = f"`{min_sec_current}`| {(percent - 1) * '─'}⚪️{(25 - percent) * '─'} | `{min_sec}`"
        embed.add_field(name="Progress", value=perbar)
        await inter.response.send_message(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(MusicCog(bot))
    print(f"> Extension {__name__} is ready")
