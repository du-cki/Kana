import discord
from discord.ext import commands
from asyncio import sleep
from datetime import datetime as dt

del_msg = {}
edit_msg = {}

class Snipe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot and not message.attachments and message.content != ".snipe":
            global del_msg
            del_msg[message.channel.id] = [message, dt.utcnow()]

            await sleep(120)
            try:
                del del_msg[message.channel.id]
            except:
                pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.author.bot and not before.attachments and before.content != after.content:
            global edit_msg
            edit_msg[before.channel.id] = [before, dt.utcnow()]

            await sleep(120)
            try:
                del edit_msg[before.channel.id]
            except:
                pass

    @commands.command()
    async def snipe(self, ctx):
        try:
            embed = discord.Embed(color=discord.Color.from_rgb(54, 57, 63), description=del_msg[ctx.channel.id][0].content, timestamp=del_msg[ctx.channel.id][1])
            embed.set_author(name=f'{del_msg[ctx.channel.id][0].author.name}#{del_msg[ctx.channel.id][0].author.discriminator}', icon_url=del_msg[ctx.channel.id][0].author.avatar.url)

            await ctx.send(embed=embed)
        except:
            await ctx.send("There is nothing for me to snipe here")

    @commands.command()
    async def esnipe(self, ctx):
        try:
            embed = discord.Embed(color=discord.Color.from_rgb(54, 57, 63), description=edit_msg[ctx.channel.id][0].content, timestamp=edit_msg[ctx.channel.id][1])
            embed.set_author(name=f'{edit_msg[ctx.channel.id][0].author.name}#{edit_msg[ctx.channel.id][0].author.discriminator}', icon_url=edit_msg[ctx.channel.id][0].author.avatar.url)

            await ctx.send(embed=embed)
        except:
            await ctx.send("There is nothing for me to esnipe here")


def setup(bot):
    bot.add_cog(Snipe(bot))
