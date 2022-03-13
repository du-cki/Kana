import discord
from discord.ext import commands

import asyncpg
import asyncio
from aiohttp import ClientSession

from os import environ, listdir
from json import load as _load

from time import time

from dotenv import load_dotenv
load_dotenv()


async def getPrefix(bot, message):
    q = await bot.pool.fetch("""
    SELECT prefix FROM prefixes WHERE id = $1;
    """, message.guild.id)

    if q:   return commands.when_mentioned_or(q[0].get("prefix"))(bot, message)

    await bot.pool.execute("""
    INSERT INTO prefixes VALUES ($1, $2);
    """, message.guild.id, ".")
    
    return commands.when_mentioned_or(".")(bot, message)


async def start(): # because im too lazy to subclass
    bot = commands.Bot(command_prefix=getPrefix, help_command=None, case_insensitive=True, intents=discord.Intents().all(), strip_after_prefix=True)
    bot._uptime = time()
    bot.session = ClientSession()
    bot.pool  = await asyncpg.create_pool(database=environ["PSQL_DATABASE"], user=environ["PSQL_USER"], password=environ["PSQL_PASSWORD"], host=environ["PSQL_HOST"])


    for filename in listdir('cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
    
    
    await bot.pool.execute("""
        CREATE TABLE IF NOT EXISTS prefixes (
        id BIGINT PRIMARY KEY,
        prefix TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
        id BIGINT,
        unix_time BIGINT,
        name TEXT
        );

        CREATE TABLE IF NOT EXISTS avatars (
        id BIGINT,
        unix_time BIGINT,
        avatar BYTEA
        );

    """)
    
    try:
        await bot.start(environ["TOKEN"], reconnect=True)
    except KeyboardInterrupt:
      await bot.logout()


    
asyncio.run(start())
