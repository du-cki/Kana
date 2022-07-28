import discord
from discord.ext import commands

import asyncio
import uvicorn  # type: ignore

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
    help_command=None,  # i'm too lazy to subclass help so i'll just disable it for the time being
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

    config = uvicorn.Config(app, port=environ.get("AVYH_PORT", 1643), log_level="info")  # type: ignore
    server = uvicorn.Server(config)  # type: ignore
    await server.serve()  # type: ignore
    await bot.close()  # this is a really janky way to close the bot after pressing ctrl + c, but it works for now. and idk a better way to do it


async def main() -> None:
    async with bot:
        bot.loop.create_task(start_server())
        await bot.start(environ["TOKEN"])


asyncio.run(main())
