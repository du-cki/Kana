import discord
from discord.ext import commands

import asyncpg
from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient

import glob
import typing
from copy import deepcopy
from cachetools import TTLCache

from os import environ
from dotenv import load_dotenv
load_dotenv()

from cogs.utils.constants import STARTUP_QUERY, VALID_EDIT_KWARGS

async def getPrefix(bot: commands.Bot, message: discord.Message):
    if not message.guild:
        return commands.when_mentioned_or("uwu")(bot, message)

    q = bot._prefixes.get(message.guild.id, None)
    if q:
        return commands.when_mentioned_or(q)(bot, message)

    await bot.pool.execute("""
    INSERT INTO prefixes
    VALUES ($1, $2);
    """, message.guild.id, "uwu")
    bot._prefixes[message.guild.id] = "uwu" # my temporary solution for now

    return commands.when_mentioned_or("uwu")(bot, message)


class KanaContext(commands.Context):
    def predict_ansi(self, target: typing.Union[discord.Member, discord.User] = None) -> bool:
        """
        Predicts whether or not the user (or author) will be able to use ANSI codes.

        :param target: The user to predict for. Defaults to the author of the message.
        :type target: discord.Member | discord.User | None

        :return: Whether or not the user will use ANSI codes.
        :rtype: bool
        """

        target = target or self.message.author

        if isinstance(target, discord.User):
            return False

        if target.is_on_mobile() \
                or target.status is discord.Status.offline:
            return False

        return True
    
    async def send(self, *args, **kwargs) -> discord.Message:
        """
        Sends a message to Context.channel.
        This is a override of :meth:`discord.abc.Messageable.send`.

        :return: The message sent.
        :rtype: discord.Message        
        """

        if kwargs.get("embed") and not kwargs.get("embed").color:
            kwargs["embed"].color = 0xE59F9F

        for embed in kwargs.get("embeds", []):
            if not embed.color:
                embed.color = 0xE59F9F

        if self.message.id in self.bot.cached_edits:
            message: discord.Message = self.channel.get_partial_message(self.bot.cached_edits[self.message.id])
            if message:
                _kwargs = deepcopy(VALID_EDIT_KWARGS)
                _kwargs["content"] = args[0] if args else None
                _kwargs.update(kwargs)
                _kwargs = {k: v for k, v in _kwargs.items() if k in VALID_EDIT_KWARGS} # thank you Leo for showing me this and helping me through the logic

                return await message.edit(**_kwargs)

        message = await super().send(*args, **kwargs)
        self.bot.cached_edits[self.message.id] = message.id
        return message

    async def reply(self, *args, **kwargs) -> discord.Message:
        """
        Replies to the message the author sent.
        This is a override of :meth:`discord.abc.Messageable.reply`.

        :return: The message sent.
        :rtype: discord.Message
        """

        if not kwargs.get("mention_author"):
            kwargs["mention_author"] = False

        return await super().reply(*args, **kwargs)


class Kana(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_context(self, message, *, cls=KanaContext):
        return await super().get_context(message, cls=cls)

    async def on_ready(self):
        print(f'{self.user} is online, on discord.py - {discord.__version__}')

    async def setup_hook(self):
        self.session = ClientSession()
        self._uptime = discord.utils.utcnow()
        self.cached_edits = TTLCache(maxsize=2000, ttl=300.0) # mapping of (command).message.id to (response).message id
        self.mongo = AsyncIOMotorClient(environ["USER_MONGO"])
        self.pool = await asyncpg.create_pool(environ["PSQL_URI"])

        await self.pool.execute(STARTUP_QUERY)

        self._prefixes = {
            prefix["id"]: prefix["prefix"]
            for prefix in (
                    await bot.pool.fetch("SELECT * FROM prefixes;")
                )
            }

        await self.load_extension("jishaku")

        for cog in glob.glob("cogs/**/*.py", recursive=True):
            cog = cog.replace("\\", ".").replace("/", ".").removesuffix(".py")
            if cog.startswith("cogs.utils"):
                continue

            await self.load_extension(cog)

    async def close(self):
        self.mongo.close()
        await super().close()
        await self.pool.close()
        self.cached_edits.clear()
        await self.session.close()


bot = Kana(
    command_prefix=getPrefix,
    help_command=None, # i'm too lazy to subclass help so i'll just disable it for the time being
    case_insensitive=True,
    intents=discord.Intents().all(),
    strip_after_prefix=True
)

bot.run(environ["TOKEN"], reconnect=True)
