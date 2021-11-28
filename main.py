import os
import json
import discord
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()


def getPrefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix=getPrefix,
                      help_command=None, case_insensitive=True)


@client.command(aliases=['re'])
@commands.is_owner()
async def reload(ctx, extension):
    try:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.channel.send(f'Reloaded `{extension}`')
    except:
        await ctx.channel.send(f'`{extension}` does not exist')


for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(os.environ["TOKEN"])
