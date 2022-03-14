import discord
from discord.ext import commands

from time import time as _time

class Yoink(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.bot:  return
        
        if before.name != after.name:
            await self.bot.pool.execute("""
            INSERT INTO users VALUES ($1, $2, $3)
            """, before.id, _time(), before.name)

        if before.avatar != after.avatar:
            ... # will complete later

    @commands.command()
    @commands.is_owner()
    async def avy(self, ctx, target: discord.Member = None):
        target = target or ctx.author

        q = await self.bot.pool.fetch("""
        SELECT name FROM users WHERE id = $1 ORDER BY unix_time DESC;
        """, target.id)
        if not q:   return await ctx.send("No records")
        
        await ctx.send(f"` {', '.join([query.get('name') for query in q])} `")


def setup(bot):
    bot.add_cog(Yoink(bot))
