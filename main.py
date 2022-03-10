import discord
from discord.ext import commands

# import asyncpg
import asyncio
from aiohttp import ClientSession

from os import listdir as _listdir
from os import environ
from json import load as _load

from time import time

from dotenv import load_dotenv
load_dotenv()

def getPrefix(bot, message):
    with open("prefixes.json", "r") as f:
        prefixes = _load(f)
    
    return commands.when_mentioned_or(prefixes.get(str(message.guild.id), "?"))(bot, message)

bot = commands.Bot(command_prefix=getPrefix, help_command=None, case_insensitive=True, intents=discord.Intents().all(), strip_after_prefix=True)
bot._uptime = time()


for filename in _listdir('cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

async def start():
    # bot.pool  = await asyncpg.create_pool(database="postgres", user=environ["USER"], password=environ["PASSWORD"], host=environ["HOST"])
    bot.session = ClientSession()
    await bot.start(environ["TOKEN"], reconnect=True)

asyncio.run(start())