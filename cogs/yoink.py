import discord
from discord.ext import commands


class Yoink(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_update(self, before : discord.Member, after : discord.Member):
        if before.bot:  return
        
        if before.name != after.name:
            await self.bot.pool.execute("""
            INSERT INTO users VALUES ($1, $2, $3)
            """, before.id, discord.utils.utcnow().timestamp(), before.name)

        if before.avatar != after.avatar:
            ... # will complete later

    @commands.command()
    @commands.is_owner()
    async def avy(self, ctx : commands.Context, target: discord.Member = None):
        """
        Get's the name history of a user.

        Parameters
        ----------
        target : discord.Member
            The user to get the name history of.
        """
        
        target = target or ctx.author

        q = await self.bot.pool.fetch("""
        SELECT name FROM users WHERE id = $1 ORDER BY unix_time DESC;
        """, target.id)
        if not q:   return await ctx.send("No records")
        
        await ctx.send(f"` {', '.join([query.get('name') for query in q])} `")


async def setup(bot):
    await bot.add_cog(Yoink(bot))
