import discord
from discord.ext import commands


class Snipe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.del_msg = {}
        self.edit_msg = {}


    @commands.Cog.listener()
    async def on_message_delete(self, message : discord.Message):
        if not message.author.bot:
            self.del_msg[message.channel.id] = [message, discord.utils.utcnow()]


    @commands.Cog.listener()
    async def on_message_edit(self, before : discord.Message, after : discord.Message):
        if not before.author.bot and before.content != after.content:
            self.edit_msg[before.channel.id] = [before, discord.utils.utcnow()]


    @commands.command()
    async def snipe(self, ctx):
        """
        Snipes the last message that was deleted from the current channel.

        """

        msg = self.del_msg.get(ctx.channel.id, None)

        if not msg:
            return await ctx.send("There is nothing for me to snipe here")

        embed = discord.Embed(color=0x2F3136, description=msg[0].content, timestamp=msg[1])
        
        if msg[0].attachments:
            embed.set_image(url=msg[0].attachments[0].url)

        embed.set_author(name=str(msg[0].author), icon_url=msg[0].author.display_avatar)
        await ctx.send(embed=embed)


    @commands.command()
    async def esnipe(self, ctx):
        """
        eSnipes the last message that was edited from the current channel.

        """

        msg = self.edit_msg.get(ctx.channel.id, None)
        if not msg:
            return await ctx.send("There is nothing for me to esnipe here")

        embed = discord.Embed(color=0x2F3136, description=msg[0].content, timestamp=msg[1])
        embed.set_author(name=str(msg[0].author), icon_url=msg[0].author.avatar.url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Snipe(bot))
