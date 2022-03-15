import discord
from discord.ext import commands
from discord import app_commands

import asyncpg
import asyncio
from aiohttp import ClientSession

from os import environ, listdir
from json import load as _load

from time import time

from dotenv import load_dotenv
load_dotenv()


async def getPrefix(bot, message):
    if isinstance(message.channel, discord.DMChannel):   return commands.when_mentioned_or(".")(bot, message)

    q = await bot.pool.fetch("""
    SELECT prefix FROM prefixes WHERE id = $1;
    """, message.guild.id)

    if q:   return commands.when_mentioned_or(q[0].get("prefix"))(bot, message)

    await bot.pool.execute("""
    INSERT INTO prefixes VALUES ($1, $2);
    """, message.guild.id, ".")
    
    return commands.when_mentioned_or(".")(bot, message)


class Kana(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._uptime = time()
        self.session = None
        self.pool = None


    async def setup_hook(self):
        print(f'{str(self.user)} is online, on d.py - {str(discord.__version__)}')

        self.session = ClientSession()
        self.pool  = await asyncpg.create_pool(database=environ["PSQL_DATABASE"], user=environ["PSQL_USER"], password=environ["PSQL_PASSWORD"], host=environ["PSQL_HOST"])

        await self.pool.execute("""
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

        for filename in listdir('cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
    
    async def close(self):
        await super().close()
        await self.pool.close()
        await self.session.close()



bot = Kana(command_prefix=getPrefix, help_command=None, case_insensitive=True, intents=discord.Intents().all(), strip_after_prefix=True)


bot.run(environ["TOKEN"], reconnect=True)
