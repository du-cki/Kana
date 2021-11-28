import requests
import discord
from discord.ext import commands


class Animals(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["meow"])
    async def cat(self, ctx):
        embed = discord.Embed(color=discord.Color.from_rgb(
            54, 57, 63), title="Meow 🐈")
        embed.set_image(url=requests.get(
            'https://aws.random.cat/meow').json().get("file"))
        embed.set_footer(text=ctx.message.author,
                         icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["quack"])
    async def duck(self, ctx):
        embed = discord.Embed(color=discord.Color.from_rgb(
            54, 57, 63), title="Quack Quack 🦆")
        embed.set_image(url=requests.get(
            'https://random-d.uk/api/random').json().get("url"))
        embed.set_footer(text=ctx.message.author,
                         icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Animals(client))
