import discord
from discord.ext import commands
from discord.ext.commands.core import has_permissions


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{str(self.bot.user)} is online, on d.py - {str(discord.__version__)}')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        q = await self.bot.pool.execute("""
        DELETE FROM prefixes WHERE id = $1
        """, guild.id)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.BotMissingPermissions):
            missing = [
                perm.replace('_', ' ').replace('guild', 'server').title()
                for perm in error.missing_perms
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
                for perm in error.missing_perms
            ]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = f'You need the `{fmt}` permission(s) to use this command.'
            return await ctx.send(_message)

        if isinstance(error, commands.CheckFailure):
            return await ctx.send("You do not have permission to use this command.")
        print(error)

    @commands.command()
    @has_permissions(administrator=True)
    async def prefix(self, ctx, prefix=None):
        if prefix is None:
            q = await self.bot.pool.fetch(f"""
            SELECT * FROM prefixes WHERE id = $1;
            """, ctx.guild.id)
            
            return await ctx.send(f"The current prefix for this server is: `{q[0].get('prefix', '?')}`")

        q = await self.bot.pool.execute("""
        UPDATE prefixes SET prefix = $1 WHERE id = $2;
        """, prefix, ctx.guild.id)

        await ctx.send(f'The prefix is now `{prefix}`')


def setup(bot):
    bot.add_cog(Events(bot))