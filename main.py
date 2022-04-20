import discord
from discord.ext import commands

import asyncpg
from aiohttp import ClientSession

import typing

from os import environ, listdir
from dotenv import load_dotenv
load_dotenv()


async def getPrefix(bot, message):
    if isinstance(message.channel, discord.DMChannel):
        return commands.when_mentioned_or("uwu")(bot, message)

    q = await bot.pool.fetch("""
    SELECT prefix FROM prefixes WHERE id = $1;
    """, message.guild.id)

    if q:
        return commands.when_mentioned_or(q[0].get("prefix"))(bot, message)

    await bot.pool.execute("""
    INSERT INTO prefixes VALUES ($1, $2);
    """, message.guild.id, "uwu")
    
    return commands.when_mentioned_or("uwu")(bot, message)

class KanaContext(commands.Context):
    def determine_ansi(self, target : typing.Union[discord.Member, discord.User] = None) -> bool:
        target = target or self.message.author
        
        if isinstance(target, discord.User):
            return False

        if target.is_on_mobile() \
            or target.status is discord.Status.offline:
                return False

        return True

class Kana(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._uptime = discord.utils.utcnow().timestamp()
        self.session = None
        self.pool = None

    async def get_context(self, message, *, cls=KanaContext):
        return await super().get_context(message, cls=cls)

    async def on_ready(self):
        print(f'{str(self.user)} is online, on discord.py - {str(discord.__version__)}')


    async def setup_hook(self):
        self.session = ClientSession()
        self.pool  = await asyncpg.create_pool(environ["PSQL_URI"])

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

        await self.load_extension("jishaku")

        environ["JISHAKU_NO_UNDERSCORE"] = "True"
        environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
        environ["JISHAKU_HIDE"] = "True"

        for filename in listdir('cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
    
    async def close(self):
        await super().close()
        await self.pool.close()
        await self.session.close()



bot = Kana(
    command_prefix=getPrefix, 
    help_command=None, # i'm too lazy to subclass help so i'll just disable it for the time being
    case_insensitive=True, 
    intents=discord.Intents().all(), 
    strip_after_prefix=True
)


bot.run(environ["TOKEN"], reconnect=True)
