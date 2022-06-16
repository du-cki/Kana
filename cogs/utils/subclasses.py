import discord
from discord.ext import commands

import asyncpg  # type: ignore
from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore

import glob
import typing
from copy import deepcopy
from cachetools import TTLCache

from .constants import STARTUP_QUERY, VALID_EDIT_KWARGS


class KanaContext(commands.Context):
    def predict_ansi(
        self, target: typing.Optional[typing.Union[discord.Member, discord.User]]
    ) -> bool:
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

        if target.is_on_mobile() or target.status is discord.Status.offline:
            return False

        return True

    async def send(self, *args, **kwargs) -> discord.Message:
        """
        Sends a message to Context.channel.
        This is a override of :meth:`discord.abc.Messageable.send`.

        :return: The message sent.
        :rtype: discord.Message
        """

        if kwargs.get("embed") and not kwargs.get("embed").color:  # type: ignore
            kwargs["embed"].color = 0xE59F9F

        for embed in kwargs.get("embeds", []):
            if not embed.color:
                embed.color = 0xE59F9F

        if self.message.id in self.bot.cached_edits:
            message: discord.Message = self.channel.get_partial_message(self.bot.cached_edits[self.message.id])  # type: ignore
            if message:
                _kwargs = deepcopy(VALID_EDIT_KWARGS)
                _kwargs["content"] = args[0] if args else None
                _kwargs.update(kwargs)
                _kwargs = {
                    k: v for k, v in _kwargs.items() if k in VALID_EDIT_KWARGS
                }  # thank you Leo for showing me this and helping me through the logic

                try:
                    return await message.edit(**_kwargs)
                except discord.HTTPException:
                    pass

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
        self.mongo_uri = kwargs.get("mongo_uri")
        self.psql_uri = kwargs.get("psql_uri")

    async def get_context(
        self, message: discord.Message, *, cls=KanaContext
    ) -> KanaContext:
        return await super().get_context(message, cls=cls)

    async def on_ready(self) -> None:
        print(f"{self.user} is online, on discord.py - {discord.__version__}")

    async def setup_hook(self) -> None:
        self.session = ClientSession()
        self._uptime = discord.utils.utcnow()
        self.mongo = AsyncIOMotorClient(self.mongo_uri)
        self.cached_edits = TTLCache(
            maxsize=2000, ttl=300.0
        )  # mapping of (command).message.id to (response).message.id
        self.pool: asyncpg.pool.Pool = await asyncpg.create_pool(self.psql_uri)  # type: ignore

        await self.pool.execute(STARTUP_QUERY)  # type: ignore

        self.prefixes: typing.Dict[int, str] = {
            prefix["guild_id"]: prefix["prefix"]
            for prefix in (
                await self.pool.fetch("SELECT guild_id, prefix FROM guild_settings;")  # type: ignore
            )
        }

        self.disabled_modules: typing.Dict[int, str] = {
            module["guild_id"]: module["disabled_modules"]
            for module in (
                await self.pool.fetch("SELECT guild_id, disabled_modules FROM guild_settings")  # type: ignore
            )
            if module["disabled_modules"] is not None
        }

        await self.load_extension("jishaku")

        for cog in glob.glob("cogs/**/*.py", recursive=True):
            cog = cog.replace("\\", ".").replace("/", ".").removesuffix(".py")
            if cog.startswith("cogs.utils"):
                continue

            await self.load_extension(cog)

    async def close(self) -> None:
        self.mongo.close()
        await super().close()
        await self.pool.close()
        self.cached_edits.clear()
        await self.session.close()
