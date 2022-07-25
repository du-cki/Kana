import discord
from discord.ext import commands

from typing import Any, List, Optional, Tuple, Union
from datetime import datetime

import imghdr

from ..utils import to_codeblock, EmbeddedPaginator, Kana, KanaContext


class Yoink(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        members: List[discord.Member] = (
            await guild.chunk(cache=True) if not guild.chunked else guild.members
        )

        for_exec: List[Tuple[Any, ...]] = []

        for member in members:  # i love data
            if (
                not hasattr(member, "mutual_guilds")
                or member.mutual_guilds
                or member is member.guild.me
            ):
                continue

            try:
                avatar = await member.display_avatar.read()
            except:  # for whatever reason it errors, we don't care.
                pass
            else:
                for_exec.append(
                    (
                        member.id,
                        discord.utils.utcnow(),
                        imghdr.what(None, avatar),
                        avatar,
                    )
                )

        sql = """
        SELECT insert_avy($1, $2, $3, $4)
        """
        await self.bot.pool.executemany(sql, for_exec)
        del for_exec

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.mutual_guilds:
            return

        avatar = await member.display_avatar.read()
        await self.bot.pool.execute(
            """
        SELECT insert_avy($1, $2, $3, $4)
        """,
            member.id,
            discord.utils.utcnow(),
            imghdr.what(None, avatar),
            avatar,
        )

    @commands.Cog.listener()
    async def on_user_avatar_update(self, _: discord.User, after: discord.User):
        avatar = await after.display_avatar.read()

        await self.bot.pool.execute(
            """
        SELECT insert_avy($1, $2, $3, $4)
        """,
            after.id,
            discord.utils.utcnow(),
            imghdr.what(None, avatar),
            avatar,
        )

    @commands.Cog.listener()
    async def on_user_name_update(self, before: discord.User, _: discord.User):
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
            self.bot.dispatch("user_name_update", before, after)

        if before.avatar != after.avatar:
            self.bot.dispatch("user_avatar_update", before, after)

        if before.discriminator != after.discriminator:
            self.bot.dispatch(
                "user_discriminator_update", before, after
            )  # currently dunder, as i don't log it yet.

    def format_time(self, time: datetime) -> str:
        return time.strftime("%a %d %b %Y %H:%M")

    @commands.command()
    async def avy(
        self,
        ctx: KanaContext,
        target: Optional[Union[discord.Member, discord.User]],
    ):
        """
        Get's the username history of a user, displays accordingly in unix time.

        :param target: The user to get the name history of.
        :type target: discord.Member, discord.User, optional
        """

        target = target or ctx.author

        query = await self.bot.pool.fetch(
            """
        SELECT name, time_changed FROM username_history
        WHERE user_id = $1
        ORDER BY time_changed DESC;
        """,
            target.id,
        )

        if not query:
            return await ctx.send("No records")

        chunks = discord.utils.as_chunks(
            [
                f'[ {self.format_time(q.get("time_changed"))} ] {q.get("name")}'
                for q in query
            ],
            10,
        )

        await EmbeddedPaginator(
            ctx,
            [to_codeblock("\n".join(chunk), "css") for chunk in chunks],
            per_page=1,
            title=f"{target.display_name}'s username History",
        ).start()


async def setup(bot: Kana):
    await bot.add_cog(Yoink(bot))
