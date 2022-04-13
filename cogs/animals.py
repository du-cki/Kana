import discord
from discord.ext import commands

class Animals(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["meow", "kitty"])
    async def cat(self, ctx : commands.Context):
        """
        Gets a random cat from the aws.random.cat API

        Parameters
        ----------
        None
        """

        async with self.bot.session.get(url="https://aws.random.cat/meow") as resp:
            resp = await resp.json(content_type="application/json")
            url = resp["file"]
        
        embed = discord.Embed(color=0x2F3136)
        embed.set_image(url=url)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["quack", "qwuak"])
    async def duck(self, ctx : commands.Context):
        """
        Gets a random duck from the random-d.uk API

        Parameters
        ----------
        None
        """
        
        async with self.bot.session.get(url="https://random-d.uk/api/random") as resp:
            resp = await resp.json(content_type="application/json")
            url = resp["url"]
        
        embed = discord.Embed(color=0x2F3136)
        embed.set_image(url=url)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Animals(bot))
