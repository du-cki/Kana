import discord
from discord.ext import commands
from asyncio import sleep
from datetime import datetime as dt


class Snipe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.del_msg = {}
        self.edit_msg = {}


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot and not message.attachments and message.content != ".snipe":
            self.del_msg[message.channel.id] = [message, dt.utcnow()]

            await sleep(120)
            try:
                del self.del_msg[message.channel.id]
            except:    pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.author.bot and not before.attachments and before.content != after.content:
            self.edit_msg[before.channel.id] = [before, dt.utcnow()]

            await sleep(120)
            try:
                del self.edit_msg[before.channel.id]
            except:    pass


    @commands.command()
    async def snipe(self, ctx):
        msg = self.del_msg.get(ctx.channel.id, None)
        if not msg:
            return await ctx.send("There is nothing for me to snipe here")

        embed = discord.Embed(color=discord.Color.from_rgb(54, 57, 63), description=msg[0].content, timestamp=msg[1])
        embed.set_author(name=str(msg[0].author), icon_url=msg[0].author.avatar.url)
        await ctx.send(embed=embed)


    @commands.command()
    async def esnipe(self, ctx):
        msg = self.edit_msg.get(ctx.channel.id, None)
        if not msg:
            return await ctx.send("There is nothing for me to esnipe here")

        embed = discord.Embed(color=discord.Color.from_rgb(54, 57, 63), description=msg[0].content, timestamp=msg[1])
        embed.set_author(name=str(msg[0].author), icon_url=msg[0].author.avatar.url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Snipe(bot))
