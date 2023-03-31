from enum import Enum

import discord
from discord.ext import commands


class Sinks(Enum):
    mp3 = discord.sinks.MP3Sink()
    wav = discord.sinks.WaveSink()
    pcm = discord.sinks.PCMSink()
    ogg = discord.sinks.OGGSink()
    mka = discord.sinks.MKASink()
    mkv = discord.sinks.MKVSink()
    mp4 = discord.sinks.MP4Sink()
    m4a = discord.sinks.M4ASink()


class RecordCog(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.connections: dict[int, discord.VoiceClient] = {}

    async def finished_callback(self, sink: discord.sinks.Sink, channel: discord.TextChannel, *args):
        recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
        print(recorded_users)
        await sink.vc.disconnect()
        files = [
            discord.File(audio.file, f"{user_id}.{sink.encoding}")
            for user_id, audio in sink.audio_data.items()
        ]
        await channel.send(
            f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files
        )

    @commands.slash_command()
    async def start_recording(self, inter: discord.ApplicationContext, sink: Sinks):
        """Record your voice!"""
        voice = inter.author.voice
        bot_voice_client = inter.guild.voice_client

        if not voice:
            text = f"{inter.user.mention}, buddy,\ngo to the voice channel"
            return await inter.send_response(content=text, ephemeral=True)

        if bot_voice_client:
            text = f"{inter.user.mention}, bot is busy"
            return await inter.send_response(content=text, ephemeral=True)
        
        vc = await voice.channel.connect()

        self.connections.update({inter.guild.id: vc})
        vc.start_recording(
            sink.value,
            self.finished_callback,
            inter.channel,
        )

        await inter.respond("The recording has started!")

    @commands.slash_command()
    async def stop_record(self, inter: discord.ApplicationContext):
        """Stop recording."""
        if inter.guild.id in self.connections:
            vc = self.connections[inter.guild.id]
            vc.stop_recording()
            del self.connections[inter.guild.id]
            await inter.delete()
        else:
            await inter.respond("Not recording in this guild.")







def setup(bot: commands.Bot):
    bot.add_cog(RecordCog(bot))
    print(f"> Extension {__name__} is ready")