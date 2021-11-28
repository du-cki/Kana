import json
import discord
from discord.ext import commands
from discord.ext.commands.core import has_permissions


class Events(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name="my daddy"))
        print(
            f'{str(self.client.user)} is online, on d.py - {str(discord.__version__)}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)

        prefixes[str(guild.id)] = "."

        with open("prefixes.json", "f") as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)

    @commands.command()
    @has_permissions(administrator=True)
    async def prefix(self, ctx, prefix):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)
        await ctx.send(f'The prefix is now `{prefix}`')

    @prefix.error
    async def prefix_error(error, ctx):
        if isinstance(error, discord.MissingPermissions):
            await ctx.send("You don't have permission to do that!")


def setup(client):
    client.add_cog(Events(client))
