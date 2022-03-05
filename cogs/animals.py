import discord
from discord.ext import commands

class Animals(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["meow", "kitty"])
    async def cat(self, ctx):
        async with self.bot.session.get(url="https://aws.random.cat/meow") as resp:
            resp = await resp.json()
            url = resp["file"]
        
        embed = discord.Embed(color=discord.Color.from_rgb(54, 57, 63))
        embed.set_image(url=url)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["quack", "qwuak"])
    async def duck(self, ctx):
        async with self.bot.session.get(url="https://random-d.uk/api/random") as resp:
            resp = await resp.json()
            url = resp["url"]
        
        embed = discord.Embed(color=discord.Color.from_rgb(54, 57, 63))
        embed.set_image(url=url)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Animals(bot))
