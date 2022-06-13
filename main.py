import discord
from discord.ext import commands

import typing

from os import environ
from dotenv import load_dotenv
load_dotenv()

from cogs.utils.subclasses import Kana

async def getPrefix(bot: Kana, message: discord.Message):
    if not message.guild:
        return commands.when_mentioned_or("uwu")(bot, message)

    q: typing.Optional[str] = bot._prefixes.get(message.guild.id, None)
    if q:
        return commands.when_mentioned_or(q)(bot, message)

    await bot.pool.execute("""
    INSERT INTO prefixes
    VALUES ($1, $2);
    """, message.guild.id, "uwu")
    bot._prefixes[message.guild.id] = "uwu" # my temporary solution for now

    return commands.when_mentioned_or("uwu")(bot, message)

bot = Kana(
    command_prefix=getPrefix,
    help_command=None, # i'm too lazy to subclass help so i'll just disable it for the time being
    case_insensitive=True,
    intents=discord.Intents().all(),
    strip_after_prefix=True,
    mongo_uri=environ["USER_MONGO"],
    psql_uri=environ["PSQL_URI"],
)

bot.run(environ["TOKEN"], reconnect=True)
