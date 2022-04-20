import discord
from discord.ext import commands


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['re'])
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, extension : str):
        """
        Reloads the specified extension.

        :param extension: The extension to reload.
        :type extension: str
        """

        try:
            await self.bot.unload_extension(f'cogs.{extension}')
            await self.bot.load_extension(f'cogs.{extension}')
            await ctx.channel.send(f'Reloaded `{extension}`')
        except discord.ext.commands.errors.ExtensionNotLoaded:
            await ctx.channel.send(f'`{extension}` does not exist')

    @commands.command(aliases=['del'])
    @commands.is_owner()
    async def delete(self, ctx: commands.Context):
        """
        Deletes the message that the author replied to.

        """

        target : discord.Message = ctx.message.reference
        if target is None:
            return await ctx.send('Reply to the message you want to delete', delete_after=5.0)

        if target.resolved.author is not ctx.guild.me:
            return await ctx.send('You can only delete messages that I sent', delete_after=5.0)

        await target.resolved.delete()


async def setup(bot):
    await bot.add_cog(Admin(bot))
