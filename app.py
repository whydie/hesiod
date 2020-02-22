import atexit
import os, shutil
import discord

from discord.ext import commands

from core import Player, Youtube
from utils import PlayerStatus
from config import TMP_PATH, TMP_NAME


bot = commands.Bot(command_prefix="-")
player = Player()


@bot.command()
async def yt(ctx, query: str = None):
    if query is None:
        await ctx.send("no")
    else:
        channel = ctx.message.author.voice.channel
        if not ctx.voice_client:
            # Connect to channel and set voice_client to Player
            player.client = await channel.connect()
            player.client.stop()

            # Search song by name
            source = Youtube.get_video(query)

            # Add new song to playlist if it's possible
            status = player.addSong(source)

            if status == PlayerStatus.FAILED:
                await ctx.send("Failed...")
            else:
                source = await discord.FFmpegOpusAudio.from_probe(f"{TMP_NAME}/{source}")
                player.client.play(source)
        else:
            await ctx.send("Я же уже, не?)")


@bot.command()
async def leave(ctx):
    await player.client.disconnect()

def clear_player():
    player.client.disconnect()

def cleanup_tmp():
    clear_player()
    folder = TMP_PATH
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

if __name__ == "__main__":
    atexit.register(cleanup_tmp)
    try:
        bot.run(os.getenv("HESIOD_TOKEN", "error"))
    except KeyboardInterrupt:
        cleanup_tmp()