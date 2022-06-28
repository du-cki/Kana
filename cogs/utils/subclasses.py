from __future__ import annotations

from typing import Dict, Optional, Type, Union, Any

import glob
from copy import deepcopy

import asyncpg
import discord
from aiohttp import ClientSession
from cachetools import TTLCache
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from typing_extensions import Self

from .constants import STARTUP_QUERY, VALID_EDIT_KWARGS


class KanaContext(commands.Context["Kana"]):
    def predict_ansi(
        self, target: Optional[Union[discord.Member, discord.User]]
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

    async def send(self, *args: Any, **kwargs: Any) -> discord.Message:
        """
        Sends a message to Context.channel.
        This is a override of :meth:`discord.ext.commands.Context.send`.

        :return: The message sent.
        :rtype: discord.Message
        """

        embed = kwargs.get("embed")
        if embed and not embed.color:
            kwargs["embed"].color = 0xE59F9F

        for embed in kwargs.get("embeds", []):
            if not embed.color:
                embed.color = 0xE59F9F

        if self.message.id in self.bot.cached_edits and not isinstance(
            self.channel, discord.GroupChannel
        ):
            message: discord.PartialMessage = self.channel.get_partial_message(
                self.bot.cached_edits[self.message.id]
            )
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

    async def reply(self, *args: Any, **kwargs: Any) -> discord.Message:
        """
        Replies to the message the author sent.
        This is a override of :meth:`discord.ext.commands.Context.send`.

        :return: The message sent.
        :rtype: discord.Message
        """

        if not kwargs.get("mention_author"):
            kwargs["mention_author"] = False

        return await super().reply(*args, **kwargs)


class Kana(commands.Bot):
    pool: asyncpg.Pool[Any]
    session: ClientSession

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.mongo_uri = kwargs.get("mongo_uri")
        self.psql_uri = kwargs.get("psql_uri")
        self._context: Type[KanaContext]

    async def get_context(
        self,
        message: Union[discord.Message, discord.Interaction],
        *,
        cls: Type[commands.Context[Self]] = KanaContext,
    ) -> KanaContext:
        return await super().get_context(message, cls=self._context)

    async def on_ready(self) -> None:
        print(f"{self.user} is online, on discord.py - {discord.__version__}")

    async def setup_hook(self) -> None:
        self.session = ClientSession()
        self.start_time = discord.utils.utcnow()
        self.mongo: AsyncIOMotorClient = AsyncIOMotorClient(self.mongo_uri)
        self.cached_edits: TTLCache[int, int] = TTLCache(
            maxsize=2000, ttl=300.0
        )  # mapping of (command).message.id to (response).message.id
        conn = await asyncpg.create_pool(self.psql_uri)

        if conn is None:
            raise RuntimeError(
                "Failed to connect to the database."
            )  # i hope this doesn't happen but this is mainly for type checking purposes

        self.pool = conn

        await self.pool.execute(STARTUP_QUERY)

        self.prefixes: Dict[int, str] = {
            prefix["guild_id"]: prefix["prefix"]
            for prefix in (
                await self.pool.fetch("SELECT guild_id, prefix FROM guild_settings;")
            )
        }

        self.disabled_modules: Dict[int, str] = {
            module["guild_id"]: module["disabled_modules"]
            for module in (
                await self.pool.fetch(
                    "SELECT guild_id, disabled_modules FROM guild_settings"
                )
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
