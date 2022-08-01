import discord
from discord.ext import commands

import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config

from os import environ
from dotenv import load_dotenv  # type: ignore

load_dotenv()

import cogs.utils.library_override  # type: ignore
from cogs.utils.subclasses import Kana
from backend import app


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
    help_command=None,  # i'm too lazy to make a proper help so i'll just disable it for the time being.
    case_insensitive=True,
    strip_after_prefix=True,
    command_prefix=getPrefix,
    psql_uri=environ["PSQL_URI"],
    intents=discord.Intents().all(),
    mongo_uri=environ["USER_MONGO"],
)


async def start_server() -> None:
    await bot.wait_until_ready()
    app.state.bot = bot
    
    config = Config()
    config.bind = "127.0.0.1:" + environ.get("AVYH_PORT", "1643")
    bot.loop.create_task(
        serve(
            app, # type: ignore
            config,
            shutdown_trigger=asyncio.Future,
        )
    )

async def main() -> None:
    async with bot:
        bot.loop.create_task(start_server())
        await bot.start(environ["TOKEN"])


asyncio.run(main())
