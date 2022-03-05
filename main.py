import discord
from discord.ext import commands

import os
import json
from time import time

from dotenv import load_dotenv
load_dotenv()

def getPrefix(bot, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    
    return commands.when_mentioned_or(prefixes.get(str(message.guild.id), "?"))(bot, message)

bot = commands.Bot(command_prefix=getPrefix, help_command=None, case_insensitive=True, intents=discord.Intents().all())
bot._uptime = time()

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(os.environ["TOKEN"])