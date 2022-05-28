import contextlib
import discord
from discord.ext import commands

import inspect
import os 

from ..utils import time as timeutil
from ..utils.constants import INVIS_CHAR

import psutil
from platform import python_version

import pygit2

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.NEW_LINE = "\n"

    def _get_uptime(self, breif: bool = False) -> str:
        return timeutil.deltaconv(int(discord.utils.utcnow().timestamp()) - int(self.bot._uptime), breif)

    @commands.command()
    async def uptime(self, ctx: commands.Context):
        """
        Gets the bot's uptime.
        """

        await ctx.send(self._get_uptime())

    async def _get_commits(self, count: int = 3) -> str:
        with contextlib.suppress(Exception):
            commits = [
                commit 
                for commit in self.repo.walk(
                    pygit2.Repository('.git').head.target,
                    pygit2.GIT_SORT_TOPOLOGICAL
                )
            ][:count]

            return "\n".join(
                [
                    f"[`{commit.hex[:6]}`](https://github.com/duckist/Kanapy/commit/{commit.hex}) {commit.message[:42] + '...' if len(commit.message) > 40 else commit.message.replace(self.NEW_LINE, '').ljust(40, INVIS_CHAR)}" 
                    for commit in commits
                ]
            )
        return "Could not retrieve commits."

    @commands.command()
    async def about(self, ctx: commands.Context):
        """
        Gets the current status of the bot.
        """

        guild = self.bot.get_guild(659189385085845515)
        owner = guild.get_member(651454696208465941) or await guild.fetch_member(651454696208465941)

        mem = psutil.Process().memory_full_info().uss / 1024**2
        cpu = psutil.Process().cpu_percent() / psutil.cpu_count()

        embed = discord.Embed(description='Latest Changes:\n' + await self._get_commits(), timestamp=discord.utils.utcnow())
        embed.set_author(name=str(owner), icon_url=owner.avatar.url, url="https://github.com/duckist")
        embed.add_field(name="Version", value=f"python-{python_version()}\ndiscord.py-{discord.__version__}", inline=True)
        embed.add_field(name="Uptime", value=self._get_uptime(breif=True), inline=True)
        embed.add_field(name="Process", value=f'{mem: .2f} MiB\n{cpu:.2f}% CPU', inline=True)

        await ctx.send(embed=embed)


    @commands.command(aliases=["src"]) 
    async def source(self, ctx: commands.Context, *, command: str = None):
        """
        Gets the source of a command, if no command is given, it will return the source of the bot.
        this was from danny's implementation of the command (https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/meta.py#L397-L435), 
        thank you danny and thank you for coming back.

        :param command: The command to get the source code of.
        :type command: str, optional
        """

        source_url = "https://github.com/duckist/Kanapy"
        if command is None:    return await ctx.send(source_url)

        obj = self.bot.get_command(command.replace(".", ""))
        if obj is None:    return await ctx.send("Could not find command")

        src = obj.callback.__code__
        module = obj.callback.__module__
        filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith('discord'):
            location = os.path.relpath(filename).replace('\\', '/')
        location = module.replace('.', '/') + '.py'

        await ctx.send(f'<{source_url}/blob/main/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>')

async def setup(bot):
    await bot.add_cog(Stats(bot))
