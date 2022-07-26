import discord
from discord.ext import commands

from os import environ
from dotenv import load_dotenv # type: ignore
load_dotenv()

from cogs.utils.subclasses import Kana
import cogs.utils.library_override # type: ignore


async def getPrefix(bot: Kana, message: discord.Message):
    if not message.guild:
        return commands.when_mentioned_or("uwu")(bot, message)

    q = bot.prefixes.get(message.guild.id, None)
    if q:
        return commands.when_mentioned_or(q)(bot, message)

    await bot.pool.execute(
        """
    INSERT INTO guild_settings
    VALUES ($1, $2);
    """,
        message.guild.id,
        "uwu",
    )
    bot.prefixes[message.guild.id] = "uwu"  # my temporary solution for now

    return commands.when_mentioned_or("uwu")(bot, message)


bot = Kana(
    help_command=None,  # i'm too lazy to subclass help so i'll just disable it for the time being
    case_insensitive=True,
    strip_after_prefix=True,
    command_prefix=getPrefix,
    psql_uri=environ["PSQL_URI"],
    intents=discord.Intents().all(),
    mongo_uri=environ["USER_MONGO"],
)

bot.run(environ["TOKEN"])
