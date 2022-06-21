import discord
from discord import app_commands
from discord.ext import commands

import typing
import asyncio

from cachetools import LRUCache

from ..utils.subclasses import Kana


ANIME_SEARCH_QUERY = """
query ($search: String) {
  Page(perPage: 10) {
    media(search: $search, type: ANIME, sort: POPULARITY_DESC) {
      id
      title {
        romaji
      }
    }
  }
}
"""

ANIME_FETCH_QUERY = """
query ($search: String) {
  Media(search: $search, type: ANIME) {
    title {
      romaji
    }
    coverImage {
      extraLarge
      color
    }
    trailer {
      site
      id
    }
    description(asHtml: false)
    genres
    averageScore
    episodes
    status
    bannerImage
    siteUrl
    isAdult
  }
}
"""


def key(interaction: discord.Interaction) -> typing.Union[discord.User, discord.Member]:
    return interaction.user


class Anidex(commands.GroupCog, name="anime"):
    def __init__(self, bot: Kana):
        self.bot = bot
        self.search_cooldown = commands.CooldownMapping.from_cooldown(1, 2, key)  # type: ignore
        self.search_cache: typing.Dict[str, typing.List[app_commands.Choice[str]]] = LRUCache(maxsize=2000)  # type: ignore

    def parse_html(self, html: str) -> str:
        return (
            html.replace("<br>", "")
            .replace("<br><br>", "\n")
            .replace("<i>", "*")
            .replace("</i>", "*")
        )

    def construct_trailer_url(
        self, data: typing.Dict[str, str]
    ) -> typing.Optional[str]:
        if data["site"] == "youtube":
            return f"https://www.youtube.com/watch?v={data['id']}"
        elif data["site"] == "dailymotion":
            return f"https://www.dailymotion.com/video/{data['id']}"

    @app_commands.command(description="Search for an anime.")
    @app_commands.describe(query="The Anime to search for.")
    async def search(self, interaction: discord.Interaction, query: str) -> None:
        await interaction.response.defer(thinking=False)
        resp: typing.Dict[str, typing.Any] = await (
            await interaction.client.session.post(  # type: ignore
                "https://graphql.anilist.co/",
                json={"query": ANIME_FETCH_QUERY, "variables": {"search": query}},
            )
        ).json()

        if resp.get("errors"):
            print(resp)  # for debugging purposes
            await interaction.edit_original_message(content="Something went wrong.")
            return

        data = resp["data"]["Media"]

        if data["isAdult"] is True and (not isinstance(interaction.channel, discord.DMChannel) or interaction.channel.is_nsfw() is False):  # type: ignore
            await interaction.edit_original_message(
                content=(
                    "The requested anime is marked as NSFW, but this channel is not NSFW."
                    "\nPlease switch to an NSFW channel to view this anime."
                    "\nOr, you can use this command in my DMs to view this anime."
                )
            )
            return

        embed = discord.Embed(
            title=data["title"]["romaji"],
            description=self.parse_html(data["description"]),
            color=discord.Color.from_str(data["coverImage"]["color"])
            if data["coverImage"]["color"]
            else 0xE6E6E6,
            url=data["siteUrl"],
        )

        embed.set_thumbnail(url=data["coverImage"].get("extraLarge"))
        embed.set_image(url=data.get("bannerImage"))

        embed.add_field(name="Genres", value=", ".join(data["genres"]))
        embed.add_field(name="Score", value=f"{data['averageScore']}/100")
        embed.add_field(name="Episodes", value=data["episodes"])
        embed.add_field(name="Status", value=data["status"].lower())

        view = None
        if data["trailer"] is not None:
            url = self.construct_trailer_url(data["trailer"])
            if url is not None:
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="Trailer", url=url))

        await interaction.edit_original_message(embed=embed, view=view)

    @search.autocomplete("query")
    async def query_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> typing.List[app_commands.Choice[str]]:
        print(f"{str(interaction.user)!r} is searching for {current}")

        if current in self.search_cache:
            return self.search_cache[current]

        retry_after = self.search_cooldown.update_rate_limit(interaction)  # type: ignore
        if retry_after:
            await asyncio.sleep(retry_after)

        resp: typing.Dict[str, typing.Any] = await (
            await interaction.client.session.post(  # type: ignore
                "https://graphql.anilist.co/",
                json={
                    "query": ANIME_SEARCH_QUERY,
                    "variables": {"search": current if current else None},
                },
            )
        ).json()

        if resp.get("errors"):
            print(resp)  # for debugging purposes
            return []

        queries = [anime["title"]["romaji"] for anime in resp["data"]["Page"]["media"]]
        results = [app_commands.Choice(name=query, value=query) for query in queries]

        self.search_cache[current] = results
        return results


async def setup(bot: Kana):
    await bot.add_cog(Anidex(bot))
