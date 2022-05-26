import discord
from discord.ext import commands

from ..utils import time

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.BotMissingPermissions):
            missing = [
                perm.replace('_', ' ').replace('guild', 'server').title()
                for perm in error.missing_permissions
            ]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            return await ctx.send(
                f'I need the `{fmt}` permissions to run this command.'
                )

        if isinstance(error, commands.MissingPermissions):
            missing = [
                perm.replace('_', ' ').replace('guild', 'server').title()
                for perm in error.missing_permissions
            ]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            return await ctx.send(
                f'You need the `{fmt}` permissions to use this command.'
                )

        if isinstance(error, commands.CheckFailure):
            return await ctx.send(
                "You do not have permission to use this command."
                )

        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.reply(
                f"You're on cooldown for `{time.deltaconv(int(error.retry_after))}`",
                mention_author=False,
                delete_after=error.retry_after if error.retry_after < 60 else None
                )

        print(error)


async def setup(bot):
    await bot.add_cog(Errors(bot))