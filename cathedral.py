import discord
from discord import Intents
from discord.ext import tasks, commands
import asyncio
from datetime import datetime
import pytz

TOKEN = ''
GUILD_ID = 1225075859333845154
CHANNEL_ID = 1289694911234310155

intents = Intents.default()
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

melody_path = 'kuranty.mp3'
moscow_tz = pytz.timezone('Europe/Moscow')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f'Не удалось найти канал с ID {CHANNEL_ID}')
        return
    await channel.connect()
    play_melody.start()

@tasks.loop(seconds=1)
async def play_melody():
    current_time = datetime.now(moscow_tz)
    if current_time.minute == 0 and current_time.second == 0:
        channel = bot.get_channel(CHANNEL_ID)
        if channel and channel.members:
            voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
            if voice_client and not voice_client.is_playing():
                voice_client.stop()
                voice_client.play(discord.FFmpegPCMAudio(melody_path))

@play_melody.before_loop
async def before_play_melody():
    await bot.wait_until_ready()

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:
        if after.channel is None or after.channel.id != CHANNEL_ID:
            await asyncio.sleep(1)
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
                if not voice_client or not voice_client.is_connected():
                    await channel.connect()
                elif voice_client.channel.id != CHANNEL_ID:
                    await voice_client.move_to(channel)

bot.run(TOKEN)
