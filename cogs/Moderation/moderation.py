import discord
from discord.ext import commands

from typing import Dict, Optional

from ..utils.subclasses import Kana, KanaContext


class Moderation(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot

    @commands.command(aliases=["wp", "mp", "mudaepurge"])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def waifupurge(self, ctx: KanaContext, amount: int = 30):
        """
        Purges a set amount of mudae's waifu posts from the current channel.

        :param amount: The amount of posts to purge, if not specified, 30 posts will be purged.
        :type amount: int, optional
        :permissions: Manage Messages
        """
        if isinstance(
            ctx.channel,
            discord.DMChannel | discord.PartialMessageable | discord.GroupChannel,
        ):  # purely for linter
            return

        if amount > 100:
            return await ctx.reply("Please enter a smaller number")

        results: Dict[str, int] = {}

        def check(message: discord.Message):
            if message.author.id == 432610292342587392 or message.content.startswith(
                "$"
            ):
                if not results.get(message.author.name):
                    results[message.author.name] = 1
                else:
                    results[message.author.name] += 1
                return True
            return False

        await ctx.channel.purge(limit=amount, check=check)
        await ctx.send(
            embed=discord.Embed(
                title="Mudae Purge Results",
                description="\n".join(f"{k} - {v}" for k, v in results.items()),
            ),
            delete_after=10,
        )

    @commands.command()
    async def prefix(self, ctx: KanaContext, prefix: Optional[str]):
        """
        Changes the guild specific prefix. if no prefix is given, it will show the current prefix.

        :param prefix: The new prefix
        :type prefix: str, optional
        :permissions: Administrator
        """
        if not ctx.guild or isinstance(
            ctx.author, discord.User
        ):  # purely for linting purposes
            return

        if prefix is None:
            return await ctx.send(
                f"The current prefix for this server is: `{self.bot.prefixes.get(ctx.guild.id, 'uwu')}`"
            )

        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])

        await self.bot.pool.execute(
            """
        UPDATE guild_settings
        SET prefix = $1
        WHERE guild_id = $2;
        """,
            prefix,
            ctx.guild.id,
        )
        self.bot.prefixes[ctx.guild.id] = prefix

        await ctx.send(f"The prefix is now `{prefix}`")


async def setup(bot: Kana):
    await bot.add_cog(Moderation(bot))
