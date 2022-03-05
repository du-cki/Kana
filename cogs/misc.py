import discord, io
from discord.ext import commands

import aiohttp
import re

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @commands.command(aliases=["yt", "ytube", "yout"])
    async def youtube(self, ctx, *, arg):
        async with self.session.get("https://www.youtube.com/results", params={"search_query": arg}) as req:
            video_ids = re.findall(r"watch\?v=(\S{11})", str(await req.read()))
        try:
            await ctx.send("https://www.youtube.com/watch?v=" + video_ids[0])
        except IndexError:
            await ctx.send("No results")



def setup(bot):
    bot.add_cog(Misc(bot))
