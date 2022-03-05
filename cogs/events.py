import discord
from discord.ext import commands
from discord.ext.commands.core import has_permissions

import json

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{str(self.bot.user)} is online, on d.py - {str(discord.__version__)}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)

        prefixes[str(guild.id)] = "."

        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

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
            await ctx.send(_message)
            return

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
            await ctx.send(_message)
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.send("You do not have permission to use this command.")
            return
        print(error)

    @commands.command()
    @has_permissions(administrator=True)
    async def prefix(self, ctx, prefix=None):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        
        if prefix is None:
            return await ctx.send(f"The current prefix for this server is: `{prefixes[str(ctx.guild.id)]}`")

        prefixes[str(ctx.guild.id)] = prefix

        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)
        await ctx.send(f'The prefix is now `{prefix}`')


def setup(bot):
    bot.add_cog(Events(bot))
