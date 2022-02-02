import discord
from discord.ext import commands

import os
import json
from time import time

from dotenv import load_dotenv
load_dotenv()

def getPrefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix=getPrefix, help_command=None, case_insensitive=True, intents=discord.Intents().all())
client._uptime = time()

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.environ["TOKEN"])
