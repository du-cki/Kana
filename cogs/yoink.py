import discord
from discord.ext import commands

from datetime import datetime

import typing

class Yoink(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_user_update(self, before : discord.Member, after : discord.Member):
        if before.bot:
            return
        
        if before.name != after.name:
            await self.bot.pool.execute("""
            INSERT INTO users VALUES ($1, $2, $3)
            """, before.id, discord.utils.utcnow().timestamp(), before.name)

        if before.avatar != after.avatar:
            ... # will complete later

    def format_time(self, time: int) -> str:
        return datetime.fromtimestamp(time).strftime("%a %d %b %Y %H:%M")
    
    @commands.command()
    @commands.is_owner()
    async def avy(self, ctx : commands.Context, target: typing.Union[discord.Member, discord.User] = None):
        """
        Get's the username history of a user, displays accordingly in unix time.
        
        :param target: The user to get the name history of.
        :type target: discord.Member, discord.User, optional
        """
        
        target = target or ctx.author

        q = await self.bot.pool.fetch("""
        SELECT name, unix_time FROM users WHERE id = $1 ORDER BY unix_time DESC;
        """, target.id)

        if not q:
            return await ctx.send("No records")

        em = discord.Embed(
            color=0x2F3136,
            description=(
                "```css\n" +
                "\n".join(
                    f'{self.format_time(q.get("unix_time"))} {q.get("name")}' for q in q
                ) +
                "```"
            )
        )
        
        await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(Yoink(bot))
