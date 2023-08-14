from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

import discord
from discord.ext import commands

import asyncio
from datetime import datetime

from io import BytesIO

from . import BaseCog, logger

if TYPE_CHECKING:
    from ._utils.subclasses import Bot


GUILD_FILESIZE_LIMIT = 25 * 1024 * 1024  # as that's what basic guilds get.


class RotatingWebhook:
    def __init__(self, webhooks: list[discord.Webhook]) -> None:
        self.webhooks = webhooks
        self.index = 0

    def get(self) -> discord.Webhook:
        if len(self.webhooks) <= self.index:
            self.index = 0

        self.index += 1

        return self.webhooks[self.index - 1]

    async def send(self, *args: Any, **kwargs: Any) -> Optional[discord.WebhookMessage]:
        await self.get().send(*args, **kwargs)


class Logger(BaseCog):
    def __init__(self, bot: "Bot"):
        super().__init__(bot)

        if self.bot.is_dev:
            logger.warning(
                "Please disable the cog `Logger`, this cog isn't intended in an development enviroment."
            )
            raise Exception

        self.webhooks = RotatingWebhook(
            [
                discord.Webhook.from_url(URL, session=self.bot.session)
                for URL in self.CONFIG["AVATAR_LOGGING"]["WEBHOOKS"]
            ]
        )

        self.ratelimit_cooldown = commands.CooldownMapping.from_cooldown(  # type: ignore
            15,
            1,
            lambda avatar: hash(
                avatar
            ),  # the docs say the ratelimits are 30 requests per 10 seconds, just to be safe i'm leaving a bit of headroom.
        )

    async def upload_avatar(
        self,
        member: discord.Member,
        file: discord.Asset,
        changed_at: datetime = discord.utils.utcnow(),
    ):
        retry = self.ratelimit_cooldown.update_rate_limit(file)  # type: ignore
        if retry:
            await asyncio.sleep(retry)
            await self.upload_avatar(member, file, changed_at)

        async with self.bot.session.get(file.url) as req:
            if req.status != 200:
                logger.error(f"Failed to fetch {member}'s avatar. {await req.text()}")
                return

            resp = await req.read()

            content_type = req.headers.get("Content-Type", "image/png")

            data = BytesIO(resp)
            if data.getbuffer().nbytes > GUILD_FILESIZE_LIMIT:
                logger.error(
                    f"AVATAR LIMIT EXCEEDED, avatar size: {data.getbuffer().nbytes}"
                )
                return

            file_ext = content_type.partition("/")[-1:][
                0
            ]  # not always accurate but it is in our usecase.

            resp = await self.webhooks.send(
                f"{member.id}\n{changed_at.timestamp()}",
                file=discord.File(data, f"{member.id}.{file_ext}"),
                wait=True,
            )

            if resp:
                await self.bot.pool.execute(
                    """
                INSERT INTO avatar_history (
                    user_id,
                    changed_at,
                    avatar_url
                ) VALUES ($1, $2, $3)
                """,
                    member.id,
                    changed_at,
                    resp.attachments[0].url,
                )

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        members = await guild.chunk() if not guild.chunked else guild.members

        for member in members:
            if member.mutual_guilds or member is guild.me:
                continue

            await self.upload_avatar(member, member.display_avatar)

    @commands.Cog.listener()
    async def on_member_avatar_update(
        self, before: discord.Member, after: discord.Member
    ):
        avatar = None
        if isinstance(before, discord.Member) and before.guild_avatar != after.guild_avatar:  # type: ignore # for some reason its a User(?) sometimes
            avatar = after.guild_avatar
        elif before.avatar != after.avatar:
            avatar = after.avatar

        if not avatar:
            avatar = after.display_avatar

        await self.upload_avatar(after, avatar)

    @commands.Cog.listener()
    async def on_member_name_update(self, before: discord.User, _: discord.User):
        await self.bot.pool.execute(
            """
        INSERT INTO username_history (user_id, time_changed, name)
            VALUES ($1, $2, $3)
        """,
            before.id,
            discord.utils.utcnow(),
            before.name,
        )

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.name != after.name:
            self.bot.dispatch("member_name_update", before, after)

        if before.avatar != after.avatar:
            self.bot.dispatch("member_avatar_update", before, after)


async def setup(bot: Bot):
    await bot.add_cog(Logger(bot))
