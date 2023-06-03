from discord.ext import commands

from typing import TYPE_CHECKING

from . import BaseCog

if TYPE_CHECKING:
    from ._utils.subclasses import Bot, Context


class Errors(BaseCog):
    @commands.Cog.listener()
    async def on_command_error(self, ctx: "Context", error: commands.CommandError):
        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.BotMissingPermissions):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_permissions
            ]
            if len(missing) > 2:
                fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = " and ".join(missing)
            return await ctx.reply(
                f"I need the `{fmt}` permissions to run this command."
            )

        if isinstance(error, commands.MissingPermissions):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_permissions
            ]
            if len(missing) > 2:
                fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = " and ".join(missing)
            return await ctx.reply(
                f"You need the `{fmt}` permissions to use this command."
            )

        if isinstance(error, commands.CheckFailure):
            return await ctx.reply("You do not have permission to use this command.")

        if isinstance(error, commands.errors.ChannelNotFound):
            return await ctx.reply(f"`{error.argument}` is not a valid channel.")

        if isinstance(error, commands.BadArgument):
            return await ctx.reply(error.args[0])

        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.reply(f"You're missing the `{error.param.name}` argument.")

        await ctx.send("Something went wrong, this incident has been reported.")
        raise error


async def setup(bot: "Bot"):
    await bot.add_cog(Errors(bot))
