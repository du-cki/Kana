from __future__ import annotations

import discord
from discord import ui
from discord.ext import commands

import asyncio

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .._utils.subclasses import Bot, Context

from .. import BaseCog, logger
from cogs.search.types import AccessToken, Album, Artist, Playlist, Song
from .spotify import InvalidToken, SearchType, search, get_token


class Dropdown(ui.Select["ResultView"]):
    def __init__(self, items: list[dict[str, str]], *args: Any, **kwargs: Any):
        self.items = items  # too lazy to type something so trivial as this.

        options = [
            discord.SelectOption(**item, default=True if _iter == 0 else False)
            for _iter, item in enumerate(self.items)
        ]

        kwargs["options"] = options
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        self.options = [
            discord.SelectOption(
                **item,
                default=True if self.values[0] == item["value"] else False,
            )
            for item in self.items
        ]

        await interaction.response.edit_message(content=self.values[0], view=self.view)


class ResultView(ui.View):
    def __init__(
        self, items: list[dict[str, str]], author_id: int, *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self.author_id = author_id
        self.original_message: Optional[discord.Message] = None

        self.add_item(Dropdown(items))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "this isn't your command dummy", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            if hasattr(child, "disabled"):
                child.disabled = True  # type: ignore

        if self.original_message:  # pesky pesky linter
            await self.original_message.edit(view=self)


class Search(BaseCog):
    def __init__(self, bot: "Bot") -> None:
        super().__init__(bot)
        self.SPOTIFY_EMOJI = self.CONFIG["Emojis"]["SPOTIFY"]
        self.spotify_auth: Optional[AccessToken] = None

    async def cog_load(self):
        if self.bot.is_dev:
            logger.warning(
                "Not starting task `restart_spotify_token_task` due to it being a development enviroment. Please manually flick it on."
            )
            return

        await self.renew_spotify_token()

    async def spotify_search(self, *args: Any, **kwargs: Any) -> Any:
        if (self.spotify_auth is None) or \
           (self.spotify_auth["accessTokenExpirationTimestampMs"] < discord.utils.utcnow().timestamp()):
                await self.renew_spotify_token()

        assert self.spotify_auth # won't ever be None but linter is mad.

        try:
            kwargs["token"] = self.spotify_auth["accessToken"]
            resp = await search(*args, **kwargs)
        except InvalidToken:
            await self.renew_spotify_token()  # because the token timesout when due to inactivity
            return await self.spotify_search(*args, **kwargs)
        else:
            return resp


    async def renew_spotify_token(self):
        logger.info("Renewing token...")

        try:
            resp = await get_token(self.bot.session)
        except:
            logger.error("Could not renew token, trying again in 5 seconds...")
            await asyncio.sleep(5)  # wait 5 seconds before trying again.
            await self.renew_spotify_token()
        else:
            logger.info(f"Succesfully renewed spotify token.")
            self.spotify_auth = resp

    @commands.group(name="spotify", aliases=["sp"], invoke_without_command=True)
    @commands.cooldown(3, 1, commands.BucketType.user)
    async def _spotify(self, ctx: Context, *, query: str):
        """
        Base command for Spotify related things. On its own it will search for songs,
        but you can search for other stuff from its sub-commands.

        Parameters
        ----------
        query: str
            The song search query.
        """
        await ctx.invoke(self._spotify_search, query=query)

    @_spotify.command(name="search", aliases=["s", "track", "tc"])
    @commands.cooldown(3, 1, commands.BucketType.user)
    async def _spotify_search(self, ctx: Context, *, query: str):
        """
        Searches songs on Spotify.

        Parameters
        ----------
        query: str
            The song search query.
        """
        session = self.bot.session

        resp: list[Song] = await self.spotify_search(
            session, query
        )

        if not resp:
            return await ctx.send("No results.")

        items: list[dict[str, str]] = []
        for item in resp:
            items.append(
                {
                    "label": item["track_name"],
                    "value": item["track_url"],
                    "description": " · ".join(
                        [artist["name"] for artist in item["artists"]]
                    )[:100],
                    "emoji": self.SPOTIFY_EMOJI,
                }
            )

        view = ResultView(items, ctx.author.id)
        view.original_message = await ctx.send(resp[0]["track_url"], view=view)

    @_spotify.command(name="artist", aliases=["art", "a"])
    @commands.cooldown(3, 1, commands.BucketType.user)
    async def _spotify_artist(self, ctx: Context, *, query: str):
        """
        Searches artists on Spotify.

        Parameters
        ----------
        query: str
            The artist search query.
        """
        session = self.bot.session

        resp: list[Artist] = await self.spotify_search(
            session, query, search_type=SearchType.artists
        )
        if not resp:
            return await ctx.send("No results.")

        items: list[dict[str, str]] = []
        for item in resp:
            items.append(
                {
                    "label": item["name"],
                    "value": item["url"],
                    "emoji": self.SPOTIFY_EMOJI,
                }
            )

        view = ResultView(items, ctx.author.id)
        view.original_message = await ctx.send(resp[0]["url"], view=view)

    @_spotify.command(name="playlist", aliases=["playlists", "pl"])
    @commands.cooldown(3, 1, commands.BucketType.user)
    async def _spotify_playlist(self, ctx: Context, *, query: str):
        """
        Searches playlists on Spotify.

        Parameters
        ----------
        query: str
            The playlist search query.
        """
        session = self.bot.session

        resp: list[Playlist] = await self.spotify_search(  # type: ignore
            session, query, search_type=SearchType.playlists
        )
        if not resp:
            return await ctx.send("No results.")

        items: list[dict[str, str]] = []
        for item in resp:
            items.append(
                {
                    "label": item["name"],
                    "value": item["url"],
                    "emoji": self.SPOTIFY_EMOJI,
                }
            )

        view = ResultView(items, ctx.author.id)
        view.original_message = await ctx.send(resp[0]["url"], view=view)

    @_spotify.command(name="album", aliases=["albums", "al"])
    @commands.cooldown(3, 1, commands.BucketType.user)
    async def _spotify_albums(self, ctx: Context, *, query: str):
        """
        Searches albums on Spotify.

        Parameters
        ----------
        query: str
            The album search query.
        """
        session = self.bot.session

        resp: list[Album] = await self.spotify_search(
            session, query, search_type=SearchType.playlists
        )
        if not resp:
            return await ctx.send("No results.")

        items: list[dict[str, str]] = []
        for item in resp:
            items.append(
                {
                    "label": item["name"],
                    "value": item["url"],
                    "emoji": self.SPOTIFY_EMOJI,
                }
            )

        view = ResultView(items, ctx.author.id)
        view.original_message = await ctx.send(resp[0]["url"], view=view)


async def setup(bot: "Bot"):
    await bot.add_cog(Search(bot))
