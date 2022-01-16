import discord
from discord.ext import commands

class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['re'])
    @commands.is_owner()
    async def reload(self, ctx, extension):
        try:
            self.client.unload_extension(f'cogs.{extension}')
            self.client.load_extension(f'cogs.{extension}')
            await ctx.channel.send(f'Reloaded `{extension}`')
        except:
            await ctx.channel.send(f'`{extension}` does not exist')


def setup(client):
    client.add_cog(Admin(client))
