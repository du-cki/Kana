import discord
from discord.ext import commands

import os
import time
import psutil
import pygit2  # pyright: ignore[reportMissingTypeStubs]
import inspect

from datetime import datetime
from platform import python_version

from typing import TYPE_CHECKING, Any, Optional

from ._utils import deltaconv
from . import BaseCog

if TYPE_CHECKING:
    from ._utils.subclasses import Bot, Context


def get_latest_commits(source_url: str, count: int = 3) -> str:
    try:
        repo = pygit2.Repository(".git")
        commits = [
            commit
            for commit in repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL)
        ][:count]

        final: str = ""
        for commit in commits:
            if len(commit.message) > 40:
                final += (
                    f"\n[ [`{commit.hex[:6]}`]({source_url}/commit/{commit.hex}) ] "
                )
                final += commit.message[:42].replace("\n", "")
                final += "..."
                final += " (<t:" + str(commit.commit_time) + ":R>)"
                continue

            final += f"\n[ [`{commit.hex[:6]}`]({source_url}/commit/{commit.hex}) ] "
            final += commit.message.replace("\n", "")
            final += " (<t:" + str(commit.commit_time) + ":R>)"

        return final
    except:
        return "Could not retrieve commits."


def format_ping(ping: float) -> str:
    if ping in range(0, 150):
        color = 32  # green
    elif ping in range(150, 200):
        color = 33  # yellow
    else:
        color = 31  # red

    return (
        f"```ansi\n\u001b[1;{color}m" + str(round(ping, 2)).ljust(30) + "\u001b[0m```"
    )


def format_time(time: datetime, **kwargs: Any):
    return deltaconv(
        int(discord.utils.utcnow().timestamp() - time.timestamp()), **kwargs
    )


class Utility(BaseCog):
    def __init__(self, bot: "Bot") -> None:
        super().__init__(bot)
        self.emojis = self.bot.config["Bot"]["Emojis"]

    @commands.hybrid_command()  # only hybrid to safe a few extra lines of code, i generally don't like slashies.
    async def ping(self, ctx: "Context"):
        """
        Retrieves the bot's ping.
        """

        start = time.perf_counter()
        mes = await ctx.send("Ping")
        end = time.perf_counter()
        message_ping = format_ping((end - start) * 1000)

        websocket = format_ping(self.bot.latency * 1000)

        start = time.perf_counter()
        await self.bot.pool.fetch("SELECT 1")
        end = time.perf_counter()
        postgres_ping = format_ping((end - start) * 1000)

        em = (
            discord.Embed(color=0xE59F9F)
            .add_field(
                name=f"{self.emojis['WEBSOCKET']} Websocket",
                value=websocket,
                inline=True,
            )
            .add_field(
                name=f"{self.emojis['CHAT_BOX']} Message",
                value=message_ping,
                inline=True,
            )
            .add_field(
                name=f"{self.emojis['POSTGRES']} Database",
                value=postgres_ping,
                inline=False,
            )
        )
        await mes.edit(content=None, embed=em)

    @commands.command()
    async def source(self, ctx: "Context", *, command: Optional[str]):
        """
        Gets the source of a command. or send the source of the bot.

        Parameters
        -----------
        command: Optional[str]
            The command to get the source of.
        """
        source = ctx.bot.config["Bot"]["SOURCE_URL"]
        if command is None:
            return await ctx.send(f"<{source}>")

        obj = self.bot.get_command(command.replace(".", ""))

        if obj is None:
            return await ctx.send("Could not find command")

        branch = ctx.bot.config["Bot"]["BRANCH"]
        if obj.cog.__class__.__name__ == "Jishaku":
            branch = "master"  # TODO: somehow get the commit hash jishaku is on.
            source = "https://github.com/Gorialis/jishaku"

        if obj.__class__.__name__ == "_HelpCommandImpl":
            return await ctx.send(
                f"no help for help yet"  # TODO: replace this when custom help is implemented.
            )

        src = obj.callback.__code__
        module = obj.callback.__module__
        filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if module.startswith("discord"):
            return

        location = os.path.relpath(filename).replace("\\", "/")
        location = module.replace(".", "/") + ".py"

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Source",
                url=f"{source}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}",
            )
        )
        await ctx.send(view=view)

    @commands.command()
    async def about(self, ctx: "Context"):
        """
        Gets the current status of the bot.
        """
        source = ctx.bot.config["Bot"]["SOURCE_URL"]
        appinfo = await ctx.bot.application_info()  # TODO: cache this

        mem = psutil.Process().memory_full_info().uss / 1024**2
        cpu = psutil.Process().cpu_percent() / psutil.cpu_count()

        embed = (
            discord.Embed(
                description=(
                    "**Latest Changes:** "
                    + get_latest_commits(source)
                    + "\n".ljust(40, "\u200b")
                ),
                timestamp=discord.utils.utcnow(),
            )
            .set_author(
                name=str(appinfo.owner),
                icon_url=appinfo.owner.display_avatar.url,
                url=source,
            )
            .add_field(
                name="Version",
                value=f"python-{python_version()}\ndiscord.py-{discord.__version__}",
            )
            .add_field(
                name="Uptime",
                value=format_time(ctx.bot.start_time, brief=True),
            )
            .add_field(
                name="Process",
                value=f"{mem:.2f} MiB\n{cpu:.2f}% CPU",
            )
        )

        await ctx.send(embed=embed)


async def setup(bot: "Bot"):
    await bot.add_cog(Utility(bot))
