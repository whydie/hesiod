import discord

from discord.ext import commands

from hesiod.media import Youtube
from hesiod.core import Player
from hesiod.config import TMP_PATH, TMP_NAME, PlayerStatus


bot = commands.Bot(command_prefix="-")
player = Player()


async def get_voice_client(ctx):
    voice_client = ctx.voice_client

    # No 'voice_client' in 'ctx' variable
    if not voice_client:
        # Connect to voice channel
        channel = ctx.message.author.voice.channel
        return await channel.connect()
    else:
        if voice_client.is_connected():
            return ctx.voice_client
        else:
            # Connect to voice channel
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

        # Create Audiource from downloaded video
        # TODO Add Song model and keep 'video_title' in an instance of song
        source = await discord.FFmpegOpusAudio.from_probe(video)
        setattr(source, "title", video_title)

        # Add new song to playlist if it's possible
        status = player.add_song(source)

        if status == PlayerStatus.SUCCESSFULLY_ADDED:
            player.play()
            await ctx.send(f"\"{video_title}\" добавлен в плейлист")

        elif status == PlayerStatus.LIST_IS_FULL:
            await ctx.send("Подожди немного...")

@bot.command()
async def song(ctx):
    player.client = await get_voice_client(ctx)
    if player.current_song:
        await ctx.send(f"Сейчас играет \"{player.current_song.title}\"")
    else:
        await ctx.send("Сейчас ничего не играет")

@bot.command()
async def playlist(ctx):
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
    player.pause()

@bot.command()
async def skip(ctx):
    player.client = await get_voice_client(ctx)
    skipped_song = player.current_song
    status = player.next_song()

    if status == PlayerStatus.SONG_CHANGED or
       status == PlayerStatus.SONG_LAST_CHANGED:
        await ctx.send(f"\"{skipped_song}\" пропущен")

    elif status == PlayerStatus.SONG_NOT_CHANGED:
        await ctx.send("Плейлист пуст")

@bot.command()
async def resume(ctx):
    player.client = await get_voice_client(ctx)
    player.resume()

@bot.command()
async def leave(ctx):
    player.client = await get_voice_client(ctx)
    await player.client.disconnect()

