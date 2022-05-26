import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command(aliases=['del'])
    async def delete(self, ctx: commands.Context):
        """
        Deletes the message that the author replied to.
        """

        target: discord.Message = ctx.message.reference
        if target is None:
            return await ctx.send('Reply to the message you want to delete', delete_after=5.0)

        if target.resolved.author is not ctx.guild.me:
            return await ctx.send('You can only delete messages that I sent', delete_after=5.0)

        await target.resolved.delete()


async def setup(bot):
    await bot.add_cog(Admin(bot))
