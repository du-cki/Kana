import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import typing

from os import environ
from dotenv import load_dotenv

load_dotenv()

from ..utils.constants import YOUTUBE
from ..utils.subclasses import Kana, KanaContext


class BaseDropdown(discord.ui.Select):
    def __init__(self, queries: dict, emoji: str):
        self.queries = queries

        options = [
            discord.SelectOption(label=channel, description=url[0], emoji=emoji)
            for channel, url in self.queries.items()
        ]

        super().__init__(placeholder="Show more...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=self.queries[self.values[0]][1])


class BaseView(discord.ui.View):
    def __init__(self, author_id: int, queries: dict, emoji: str):
        super().__init__(timeout=60)
        self.add_item(BaseDropdown(queries, emoji))
        self.author_id = author_id
        self.response: discord.Message = None  # type: ignore

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "this isn't your command dummy", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        for children in self.children:
            children.disabled = True  # type: ignore
        await self.response.edit(view=self)


class Search(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot

    @commands.command(aliases=["yt"])
    @commands.cooldown(1, 5, BucketType.user)
    async def youtube(self, ctx: KanaContext, *, query: typing.Optional[str]):
        """
        Searches YouTube for a video, if no query is given, it will send a link to youtube.

        :param query: The query to search for.
        :type query: str, optional
        """

        if not query:
            return await ctx.send("https://www.youtube.com/")

        q = await self.bot.session.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "key": environ["YOUTUBE_KEY"],
                "q": query,
                "part": "snippet",
                "type": "video",
                "maxResults": 10,
            },
        )

        if not q:
            return await ctx.send("No results found")

        q = await q.json()

        parsed_queries = {
            item["snippet"]["channelTitle"][:100]: [
                item["snippet"]["title"][:100],
                "https://www.youtube.com/watch?v=" + item["id"]["videoId"],
            ]
            for item in q["items"]
        }

        view = BaseView(ctx.author.id, parsed_queries, YOUTUBE)
        view.response = await ctx.send(list(parsed_queries.values())[0][1], view=view)


async def setup(bot):
    await bot.add_cog(Search(bot))
