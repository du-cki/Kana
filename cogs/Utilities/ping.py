import discord
from discord.ext import commands
from discord import app_commands

import time

from ..utils.constants import WEBSOCKET, CHAT_BOX, POSTGRES

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _format_ping(self, ping : int) -> str:
        p = f"```diff\n{'-' if ping > 150 else '+'} {round(ping)}ms"
        return p.ljust(30) + "```"

    @commands.command()
    async def ping(self, ctx : commands.Context):
        """
        Gets the bot's latency.
        """

        start = time.perf_counter()
        mes = await ctx.send("Ping")
        end = time.perf_counter()
        message_ping = self._format_ping((end - start) * 1000)

        websocket = self._format_ping(self.bot.latency * 1000)

        start = time.perf_counter()
        await self.bot.pool.fetch("SELECT 1")
        end = time.perf_counter()
        postgres_ping = self._format_ping((end - start) * 1000)

        em = discord.Embed() \
                    .add_field(name=f"{WEBSOCKET} Websocket", value=websocket, inline=True) \
                        .add_field(name=f"{CHAT_BOX} Message", value=message_ping, inline=True) \
                            .add_field(name=f"{POSTGRES} Database", value=postgres_ping, inline=False) \
        
        await mes.edit(content=None, embed=em)

    @app_commands.command(name="ping", description="Get's the bot's latency!")
    async def _ping(self, interaction: discord.Interaction):
        """
        Gets the bot's latency.
        """

        start = time.perf_counter()
        await interaction.response.send_message("Ping")
        end = time.perf_counter()
        interaction_ping = self._format_ping((end - start) * 1000)

        websocket = self._format_ping(self.bot.latency * 1000)

        start = time.perf_counter()
        await self.bot.pool.fetch("SELECT 1")
        end = time.perf_counter()
        postgres_ping = self._format_ping((end - start) * 1000)

        em = discord.Embed() \
                    .add_field(name=f"{WEBSOCKET} Websocket", value=websocket, inline=True) \
                        .add_field(name=f"{CHAT_BOX} Interaction", value=interaction_ping, inline=True) \
                            .add_field(name=f"{POSTGRES} Database", value=postgres_ping, inline=False) \

        await interaction.edit_original_message(content=None, embed=em)
        

async def setup(bot):
    await bot.add_cog(Ping(bot))
