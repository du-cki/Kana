import discord
from discord.ext import commands

from ..utils.subclasses import Kana, KanaContext

class Animals(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot

    @commands.command(aliases=["meow", "kitty"])
    async def cat(self, ctx: KanaContext):
        """
        Gets a random cat from the thecatapi.com API.
        """

        async with self.bot.session.get(url="https://api.thecatapi.com/v1/images/search") as resp:
            resp = await resp.json(content_type="application/json")
            url = resp[0]['url']
        
        embed = discord.Embed().set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["quack", "qwuak"])
    async def duck(self, ctx: KanaContext):
        """
        Gets a random duck from the random-d.uk API.
        """

        async with self.bot.session.get(url="https://random-d.uk/api/random") as resp:
            resp = await resp.json(content_type="application/json")
            url = resp["url"]
        
        embed = discord.Embed().set_image(url=url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Animals(bot))
