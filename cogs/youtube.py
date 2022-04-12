import discord
from discord.ext import commands

from youtube_search import YoutubeSearch


class YoutubeDropdown(discord.ui.Select):
    def __init__(self, queries : dict):
        self.queries = queries

        options = []
        for channel, url in self.queries.items():
            options.append(discord.SelectOption(label=channel, description=url[0], emoji='<:youtube_logo:940649600920985691>'))
        
        super().__init__(placeholder='Show more...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=self.queries[self.values[0]][1])


class YoutubeView(discord.ui.View):
    def __init__(self, author_id : int, queries : dict):
        super().__init__(timeout=60)
        self.add_item(YoutubeDropdown(queries))
        self.author_id = author_id
        self.response = None

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This is not your command dummy", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        await self.response.edit(view=None)


class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["yt", "ytube", "yout"])
    async def youtube(self, ctx : commands.Context, *, query : str):
        """
        Searches YouTube for a video.

        Parameters
        ----------
        query : str
            The query to search YouTube for.
        """

        q = YoutubeSearch(query, max_results=10).to_dict()

        if not q:
            return await ctx.send("No results found")
        
        parsed_queries = {}
        for item in q:
            parsed_queries[item["channel"]] = [item["title"], "https://youtube.com" + str(item["url_suffix"])]
        
        view = YoutubeView(ctx.author.id, parsed_queries)
        mes = await ctx.send(list(parsed_queries.values())[0][1], view=view)
        view.response = mes


async def setup(bot):
    await bot.add_cog(Youtube(bot))
