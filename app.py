import atexit
import os, shutil
import discord

from discord.ext import commands

from core import Player, Youtube
from utils import PlayerStatus, clear_tmp
from config import TMP_PATH, TMP_NAME


bot = commands.Bot(command_prefix="-")
player = Player()

async def get_voice_client(ctx):
    voice_client = ctx.voice_client
    if not voice_client:
        channel = ctx.message.author.voice.channel
        return await channel.connect()
    else:
        if voice_client.is_connected():
            return ctx.voice_client
        else:
            channel = ctx.message.author.voice.channel
            return await channel.connect()

@bot.command()
async def yt(ctx, query: str = None):
    if query is None:
        await ctx.send("Example: -yt yAv5pLO37mE")
    else:
        # Connect to channel and set voice_client to Player
        player.client = await get_voice_client(ctx)

        # Download video from youtube
        video, video_title = Youtube.get_video(query)

        # Create AudioSource from downloaded video
        source = await discord.FFmpegOpusAudio.from_probe(video)
        setattr(source, "title", video_title)

        # Add new song to playlist if it's possible
        status = player.addSong(source)

        if status == PlayerStatus.SUCCESSFULLY_ADDED:
            if not player.client.is_playing():
                player.play()
            await ctx.send(f"\"{video_title}\" добавлен в плейлист")

        elif status == PlayerStatus.LIST_IS_FULL:
            await ctx.send("Подожди немного...")

@bot.command()
async def song(ctx):
    player.client = await get_voice_client(ctx)
    if player.client.is_playing():
        await ctx.send(f"Сейчас играет \"{player.current_song.title}\"")
    else:
        await ctx.send("Сейчас ничего не играет")

@bot.command()
async def playlist(ctx):
    player.client = await get_voice_client(ctx)
    current_song = player.current_song
    embed = discord.Embed(
        title="Hesiod"
    )
    message = "1. " + current_song.title
    for i, song in enumerate(player.playlist, start=2):
        message += f"\n{i}. {song.title}"

    embed.add_field(name="Плейлист", value=message, inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def pause(ctx):
    player.client = await get_voice_client(ctx)
    player.client.pause()

@bot.command()
async def skip(ctx):
    player.client = await get_voice_client(ctx)
    skipped_song = player.current_song
    status = player.next_song()

    if status == PlayerStatus.SONG_SKIPPED:
        await ctx.send(f"\"{skipped_song}\" пропущен")

    elif status == PlayerStatus.SONG_NOT_SKIPPED:
        await ctx.send("Плейлист пуст")

@bot.command()
async def resume(ctx):
    player.client = await get_voice_client(ctx)
    player.client.resume()

@bot.command()
async def leave(ctx):
    player.client = await get_voice_client(ctx)
    await player.client.disconnect()

@bot.command()
async def voting(ctx, type):
    player.client = await get_voice_client(ctx)

    if not player.client.is_playing():
        if type == "start":
            song = await discord.FFmpegOpusAudio.from_probe("voting_start.mp3")
        
        elif type == "end":
            song = await discord.FFmpegOpusAudio.from_probe("voting_end.mp3")

        player.client.play(song)
    else:
        await ctx.send("ГОЛОСОВАНИЕ ЗАПРЕЩЕНО (играет музыка)")

if __name__ == "__main__":
    atexit.register(clear_tmp)
    try:
        bot.run(os.getenv("HESIOD_TOKEN", "error"))
    except KeyboardInterrupt:
        clear_tmp()