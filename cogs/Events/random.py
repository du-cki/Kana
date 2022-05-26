import discord
from discord.ext import commands

from ..utils import time

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        await self.bot.pool.execute("""
        DELETE FROM prefixes WHERE id = $1
        """, guild.id)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content != after.content:
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)

async def setup(bot):
    await bot.add_cog(Events(bot))