import discord
from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.channel.send(f"Pong! `{round(self.bot.latency * 1000)}ms`")

    @app_commands.command(name="ping", description="Get's the bot's latency!")
    async def _ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! `{round(self.bot.latency * 1000)}ms`")

async def setup(bot):
    await bot.add_cog(Ping(bot))
