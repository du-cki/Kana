import discord
from discord.ext import commands


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild : discord.Guild):
        await self.bot.pool.execute("""
        DELETE FROM prefixes WHERE id = $1
        """, guild.id)

    @commands.Cog.listener()
    async def on_message_edit(self, before : discord.Message, after : discord.Message):
        if before.content != after.content:
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_command_error(self, ctx : commands.Context, error):
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
            _message = f'I need the `{fmt}` permission(s) to run this command.'
            return await ctx.send(_message)

        if isinstance(error, commands.MissingPermissions):
            missing = [
                perm.replace('_', ' ').replace('guild', 'server').title()
                for perm in error.missing_permissions
            ]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = f'You need the `{fmt}` permission(s) to use this command.'
            return await ctx.send(_message)

        if isinstance(error, commands.CheckFailure):
            return await ctx.send("You do not have permission to use this command.")
        
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.reply(f"you are on cooldown for {error.retry_after:.2f} seconds", mention_author=False)

        print(error)


async def setup(bot):
    await bot.add_cog(Events(bot))