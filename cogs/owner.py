import discord
from discord.ext import commands


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['re'])
    @commands.is_owner()
    async def reload(self, ctx, extension):
        try:
            await self.bot.unload_extension(f'cogs.{extension}')
            await self.bot.load_extension(f'cogs.{extension}')
            await ctx.channel.send(f'Reloaded `{extension}`')
        except discord.ext.commands.errors.ExtensionNotLoaded:
            await ctx.channel.send(f'`{extension}` does not exist')


async def setup(bot):
    await bot.add_cog(Admin(bot))
