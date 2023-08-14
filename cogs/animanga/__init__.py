import discord
from discord import ui
from discord import app_commands

from .. import BaseCog

from .anilist import fetch, search_auto_complete
from .types import FetchResult, SEARCH_TYPE

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._utils.subclasses import Bot


def create_embed(data: FetchResult) -> discord.Embed:
    embed = discord.Embed(
        title=data["title"],
        description=data["description"],
        color=discord.Color.from_str(data["color"]) if data["color"] else 0xE6E6E6,
        url=data["siteUrl"],
    )

    embed.set_thumbnail(url=data["coverImage"])
    embed.set_image(url=data["bannerImage"])
    embed.add_field(name="Genres", value=", ".join(data["genres"]))
    embed.add_field(name="Score", value=f"{data['averageScore']}/100")
    embed.add_field(name="Status", value=data["status"])

    return embed


async def check_nsfw(interaction: discord.Interaction, result: FetchResult):
    assert interaction.channel, "`Interaction.channel` seems to be `None`."

    if result["isAdult"] and not (
        isinstance(interaction.channel, discord.DMChannel | discord.PartialMessageable)
        or interaction.channel.is_nsfw()
    ):
        show_type = interaction.command.parent.name.lower()  # type: ignore # the errors shown should not be an issue.
        return await interaction.edit_original_response(
            content=(
                f"The requested {show_type} has been marked as NSFW. To view it, "
                "please switch to an NSFW channel or re-use the command in my DMs."
            )
        )


class AniManga(BaseCog):
    anime = app_commands.Group(
        name="anime",
        description="...",
    )

    @anime.command(name="search")
    @app_commands.autocomplete(query=search_auto_complete)
    async def anime_search(self, interaction: discord.Interaction, query: str):
        """
        Search for an Anime.

        Parameters
        -----------
        query: str
            The Anime to search for.
        """
        await interaction.response.defer(thinking=False)

        result = await fetch(self.bot.session, query, SEARCH_TYPE.ANIME)
        if not result:
            return await interaction.edit_original_response(content="No anime found.")

        nsfw = await check_nsfw(interaction, result)
        if nsfw:
            return

        embed = create_embed(result)

        if result["episodes"]:
            embed.add_field(name="Episodes", value=result["episodes"])

        if result["studios"]:
            embed.add_field(
                name="Studio",
                value=result["studios"][0][
                    "formatted"
                ],  # always going to be the main studio
            )

        view = None

        trailer = result["trailer"]
        if trailer:
            view = view or ui.View()
            view.add_item(ui.Button(label="Trailer", url=trailer.strip()))

        await interaction.edit_original_response(embed=embed, view=view)

    manga = app_commands.Group(
        name="manga",
        description="...",
    )

    @manga.command(name="search")
    @app_commands.autocomplete(query=search_auto_complete)
    async def manga_search(self, interaction: discord.Interaction, query: str):
        """
        Search for a Manga.

        Parameters
        -----------
        query: str
            The Manga to search for.
        """

        assert interaction.channel, "`Interaction.channel` seems to be `None`."

        await interaction.response.defer(thinking=False)

        result = await fetch(self.bot.session, query, SEARCH_TYPE.MANGA)
        if not result:
            return await interaction.edit_original_response(content="No Manga found.")

        nsfw = await check_nsfw(interaction, result)
        if nsfw:
            return

        embed = create_embed(result)

        if result["chapters"]:
            embed.add_field(name="Chapters", value=result["chapters"])

        await interaction.edit_original_response(embed=embed)


async def setup(bot: "Bot"):
    await bot.add_cog(AniManga(bot))
