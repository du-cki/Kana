import discord
from discord.ext import commands

import typing
from cachetools import TTLCache

from ..utils.subclasses import Kana, KanaContext

class Snipe(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot
        self.del_msg = TTLCache(maxsize=2000, ttl=120)
        self.edit_msg = TTLCache(maxsize=2000, ttl=120)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.author.bot:
            self.del_msg[message.channel.id] = [message, discord.utils.utcnow()]

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.author.bot and before.content != after.content:
            self.edit_msg[before.channel.id] = [before, discord.utils.utcnow()]

    @commands.command()
    async def snipe(self, ctx: commands.Context, target: typing.Optional[discord.TextChannel]): # type: ignore
        """
        Snipes the last message that was deleted from the mentioned channel, or the current channel if no channel is mentioned.

        :param target: The channel to snipe from.
        :type target: discord.TextChannel, optional
        """
        target: discord.TextChannel = target or ctx.channel # type: ignore
        msg = self.del_msg.get(target.id, None)

        if not msg:
            return await ctx.send(f"There is nothing for me to snipe {'here' if target is ctx.channel else f'in {target.mention}'}.")

        embed = discord.Embed(description=msg[0].content, timestamp=msg[1])
        
        if msg[0].attachments:
            embed.set_image(url=msg[0].attachments[0].url)

        embed.set_author(name=str(msg[0].author), icon_url=msg[0].author.display_avatar)
        await ctx.send(embed=embed)

    @commands.command()
    async def esnipe(self, ctx: commands.Context, target: typing.Optional[discord.TextChannel]): # type: ignore
        """
        E(dit)-Snipes the last message that was edited from the mentioned channel, or the current channel if no channel is mentioned.

        :param target: The channel to E(dit)-Snipes from.
        :type target: discord.TextChannel, optional
        """
        target: discord.TextChannel = target or ctx.channel # type: ignore
        msg = self.edit_msg.get(target.id, None)
        if not msg:
            return await ctx.send(f"There is nothing for me to esnipe {'here' if target is ctx.channel else f'in {target.mention}'}.")

        embed = discord.Embed(description=msg[0].content, timestamp=msg[1])
        embed.set_author(name=str(msg[0].author), icon_url=msg[0].author.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Snipe(bot))
