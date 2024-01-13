import discord
from discord import ui, app_commands

from urllib.parse import quote

from .. import BaseCog

from .anilist import AniList
from .types import FetchResult, Relation, SearchType

from typing import TYPE_CHECKING, Any, Optional, Self

if TYPE_CHECKING:
    from .._utils.subclasses import Bot


NSFW_ERROR_MSG = (
    "The requested **%s** has been marked as NSFW. "
    "Switch to an NSFW channel or re-run the command in my DMs."
)


class PrivateView(ui.View):
    message: discord.InteractionMessage

    def __init__(self, author: int, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.author = author

    async def interaction_check(self, itx: discord.Interaction) -> bool:
        if not itx.user.id == self.author:
            await itx.response.send_message(
                f"This search belongs to `<@{self.author}>`, run the command yourself to use this.",
                ephemeral=True,
            )
            return False

        return True

    async def on_timeout(self):
        for child in self.children:
            if hasattr(child, "disabled"):
                child.disabled = True  # type: ignore

        await self.message.edit(view=self)


class RelationSelect(ui.Select[ui.View]):
    def __init__(self, relations: list[Relation], *args: Any, **kwargs: Any):
        super().__init__(
            options=self._to_options(relations),
            placeholder="Related Media",
            *args,
            **kwargs,
        )

    def _to_options(self, relations: list[Relation]) -> list[discord.SelectOption]:
        return [
            discord.SelectOption(
                label=relation["title"],
                description=relation["relation_type"].replace("_", " ").title(),
                emoji="\U0001f4d6" if relation["type"] == "MANGA" else "\U0001f3a5",
                value=f"{relation['type']}_{relation['id']}",
            )
            for relation in relations
        ][:25]

    async def _query_anilist(
        self,
        interaction: discord.Interaction["Bot"],
        search_id: str,
        search_type: str,
        *,
        attempt: int = 0,
    ) -> Optional[FetchResult]:
        result = await interaction.client.anilist.fetch(
            f"x (ID: {search_id})",  # bit jank but who is gonna stop me
            search_type=SearchType.ANIME
            if search_type == "ANIME"
            else SearchType.MANGA,
        )

        if not result and attempt < 3:
            return await self._query_anilist(
                interaction, search_id, search_type, attempt=attempt
            )

        return result

    async def callback(self, interaction: discord.Interaction["Bot"]):  # type: ignore
        await interaction.response.defer()
        search_type, search_id = self.values[0].split("_")

        result = await self._query_anilist(interaction, search_id, search_type)

        if not result:
            return await interaction.edit_original_response(view=self.view)

        self.options = (
            self._to_options(result["relations"]) if result["relations"] else []
        )

        assert self.view

        self.view.clear_items()
        self.view.add_item(self)

        if result["trailer"]:
            self.view.add_item(
                ui.Button(label="Trailer", url=result["trailer"].strip())
            )

        await interaction.edit_original_response(embed=AnimangaEmbed.from_data(result))


class AnimangaEmbed(discord.Embed):
    @classmethod
    def from_data(cls, data: FetchResult) -> Self:
        embed = cls(
            title=data["title"],
            description=data["description"],
            color=discord.Color.from_str(data["color"]) if data["color"] else 0xE6E6E6,
            url=data["siteUrl"],
        )

        embed.set_thumbnail(url=data["coverImage"])
        embed.set_image(url=data["bannerImage"])

        embed.add_field(
            name="Genres",
            value=", ".join(
                f"[{genre}](https://anilist.co/search/{data['type'].name.lower()}?genres={quote(genre)})"
                for genre in data["genres"]
            ),
        )
        embed.add_field(
            name="Score",
            value=f"{data['averageScore']}/100" if data["averageScore"] else "NaN",
        )
        embed.add_field(name="Status", value=data["status"])

        if data["episodes"]:
            embed.add_field(name="Episodes", value=data["episodes"])

        if data["studios"]:
            embed.add_field(
                name="Studio",
                value=data["studios"][0][
                    "formatted"
                ],  # always going to be the main studio
            )

        if data["chapters"]:
            embed.add_field(name="Chapters", value=data["chapters"])

        return embed


def is_nsfw(interaction: discord.Interaction, result: FetchResult) -> bool:
    assert interaction.channel

    if result["isAdult"] and not (
        isinstance(
            interaction.channel,
            discord.DMChannel | discord.PartialMessageable | discord.GroupChannel,
        )
        or interaction.channel.is_nsfw()
    ):
        return True

    return False


class AniManga(BaseCog):
    def __init__(self, bot: "Bot"):
        super().__init__(bot)
        self.anilist = self.bot.anilist

    anime = app_commands.Group(
        name="anime",
        description="...",
    )

    @anime.command(name="search")
    @app_commands.autocomplete(query=AniList.search_auto_complete)
    async def anime_search(self, interaction: discord.Interaction, query: str):
        """
        Search for an Anime.

        Parameters
        -----------
        query: str
            The Anime to search for.
        """
        await interaction.response.defer()

        result = await self.anilist.fetch(query, search_type=SearchType.ANIME)
        if not result:
            return await interaction.edit_original_response(content="No anime found.")

        if is_nsfw(interaction, result):
            return await interaction.edit_original_response(
                content=NSFW_ERROR_MSG % "anime"
            )

        embed = AnimangaEmbed.from_data(result)

        view = None
        if result["relations"]:
            view = view or PrivateView(interaction.user.id)
            view.add_item(RelationSelect(result["relations"]))

        if result["trailer"]:
            view = view or PrivateView(interaction.user.id)
            view.add_item(ui.Button(label="Trailer", url=result["trailer"].strip()))

        if not view:
            return await interaction.edit_original_response(embed=embed)

        view.message = await interaction.edit_original_response(embed=embed, view=view)

    manga = app_commands.Group(
        name="manga",
        description="...",
    )

    @manga.command(name="search")
    @app_commands.autocomplete(query=AniList.search_auto_complete)
    async def manga_search(self, interaction: discord.Interaction, query: str):
        """
        Search for a Manga.

        Parameters
        -----------
        query: str
            The Manga to search for.
        """
        await interaction.response.defer()

        result = await self.anilist.fetch(query, search_type=SearchType.MANGA)
        if not result:
            return await interaction.edit_original_response(content="No Manga found.")

        if is_nsfw(interaction, result):
            return await interaction.edit_original_response(
                content=NSFW_ERROR_MSG % "manga"
            )

        embed = AnimangaEmbed.from_data(result)
        await interaction.edit_original_response(embed=embed)


async def setup(bot: "Bot"):
    await bot.add_cog(AniManga(bot))
