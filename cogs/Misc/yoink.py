import discord
from discord.ext import commands

from ..utils.markdown import to_codeblock
from datetime import datetime

import typing

class Yoink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_name_update(self, before: discord.User, _: discord.User):
        if before.bot:
            return

        await self.bot.pool.execute("""
        INSERT INTO users VALUES ($1, $2, $3)
        """, before.id, discord.utils.utcnow().timestamp(), before.name)


    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.name != after.name:
            self.bot.dispatch("user_name_update", before, after)

        if before.avatar != after.avatar:
            self.bot.dispatch("user_avatar_update", before, after)

    def format_time(self, time: int) -> str:
        return datetime.fromtimestamp(time).strftime("%a %d %b %Y %H:%M")
    
    @commands.command()
    @commands.is_owner()
    async def avy(self, ctx: commands.Context, target: typing.Union[discord.Member, discord.User] = None):
        """
        Get's the username history of a user, displays accordingly in unix time.
        
        :param target: The user to get the name history of.
        :type target: discord.Member, discord.User, optional
        """
        
        target = target or ctx.author

        q = await self.bot.pool.fetch("""
        SELECT name, unix_time FROM users 
        WHERE id = $1 
        ORDER BY unix_time DESC;
        """, target.id)

        if not q:
            return await ctx.send("No records")

        description = to_codeblock(
                        "\n".join(
                            f'[ {self.format_time(q.get("unix_time"))} ] {q.get("name")}' for q in q
                        ), "css"
                    )

        em = discord.Embed(description=description)
        
        await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(Yoink(bot))
