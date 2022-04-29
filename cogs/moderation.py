import discord
from discord.ext import commands

from contextlib import suppress

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["wp"])
    @commands.has_permissions(manage_messages=True)
    async def waifupurge(self, ctx : commands.Context, amount : int = 30):
        """
        Purges a set amount of mudae's waifu posts from the current channel.

        :param amount: The amount of posts to purge, if not specified, 30 posts will be purged.
        :type amount: int, optional
        :permissions: Manage Messages
        """

        if amount > 50:
            return await ctx.reply("Please enter a smaller number")

        def check(m):
            return (m.author.id == 432610292342587392 or m.content.startswith("$"))
            
        await ctx.channel.purge(limit=amount, check=check)
        with suppress(Exception):
            await ctx.message.add_reaction('\u2705')

    @commands.command()
    @commands.guild_only()
    async def prefix(self, ctx : commands.Context, prefix : str = None):
        """
        Changes the guild specific prefix. if no prefix is given, it will show the current prefix.

        :param prefix: The new prefix
        :type prefix: str, optional
        :permissions: Administrator
        """

        if prefix is None:
            return await ctx.send(f"The current prefix for this server is: `{self.bot._prefixes.get(ctx.guild.id, 'uwu')}`")

        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(['administrator'])

        await self.bot.pool.execute("""
        UPDATE prefixes SET prefix = $1 WHERE id = $2;
        """, prefix, ctx.guild.id)

        self.bot._prefixes[ctx.guild.id] = prefix

        await ctx.send(f'The prefix is now `{prefix}`')


async def setup(bot):
    await bot.add_cog(Moderation(bot))
