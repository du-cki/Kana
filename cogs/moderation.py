import discord
from discord.ext import commands

from contextlib import suppress

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["wp"])
    @commands.has_permissions(manage_messages=True)
    async def waifupurge(self, ctx, amount=30):
        if amount > 50: return await ctx.reply("Please enter a smaller number")

        def check(m):
            return (m.author.id == 432610292342587392 or m.content.startswith("$"))
            
        await ctx.channel.purge(limit=amount, check=check)
        with suppress(Exception):
            await ctx.message.add_reaction('\u2705')

    @commands.command()
    async def prefix(self, ctx, prefix=None):
        if prefix is None:
            q = await self.bot.pool.fetch(f"""
            SELECT * FROM prefixes WHERE id = $1;
            """, ctx.guild.id)
            
            return await ctx.send(f"The current prefix for this server is: `{q[0].get('prefix', 'uwu')}`")

        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(['administrator'])

        q = await self.bot.pool.execute("""
        UPDATE prefixes SET prefix = $1 WHERE id = $2;
        """, prefix, ctx.guild.id)

        await ctx.send(f'The prefix is now `{prefix}`')



async def setup(bot):
    await bot.add_cog(Moderation(bot))
