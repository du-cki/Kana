import discord
from discord.ext import commands

import typing
from cachetools import TTLCache

import contextlib

from ..utils.subclasses import Kana, KanaContext

class Snipe(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot
        self.del_msg = TTLCache(maxsize=2000, ttl=120)
        self.edit_msg = TTLCache(maxsize=2000, ttl=120)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild:
            return

        if not message.author.bot and 'snipe' not in self.bot.disabled_modules.get(message.guild.id, []):
            self.del_msg[message.channel.id] = (message, discord.utils.utcnow())

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, _: discord.Message):
        if not before.guild:
            return

        if not before.author.bot and 'snipe' not in self.bot.disabled_modules.get(before.guild.id, []):
            self.edit_msg[before.channel.id] = (before, discord.utils.utcnow())

    @commands.command()
    async def snipe(self, ctx: KanaContext, target: typing.Optional[discord.TextChannel]): # type: ignore
        """
        Snipes the last message that was deleted from the mentioned channel, or the current channel if no channel is mentioned.

        :param target: The channel to snipe from.
        :type target: discord.TextChannel, optional
        """
        if not ctx.guild:
            return

        if 'snipe' in self.bot.disabled_modules.get(ctx.guild.id, []):
            return await ctx.send("Sniping is disabled in this server.")

        target: discord.TextChannel = target or ctx.channel # type: ignore
        msg = self.del_msg.get(target.id, None)

        if not msg:
            return await ctx.send(f"There is nothing for me to snipe {'here' if target is ctx.channel else f'in {target.mention}'}.")

        message, timestamp = msg
        embeds = []
        embed = discord.Embed(description=message.content, timestamp=timestamp)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar)
        embeds.append(embed)

        attachments = message.attachments
        if attachments:
            embed.set_image(url=f"attachment://{attachments[0].filename}")
            try:
                attachments.pop()
            except KeyError:
                pass
            else:
                for attachment in attachments:
                    embeds.append(
                        discord.Embed(
                            description=f"[{attachment.filename}]({attachment.url})").set_image(
                                url=f"attachment://{attachment.filename}" if not attachment.is_spoiler() else None
                                )
                        )

        await ctx.send(
            embeds=embeds,
            files=[
                await attachment.to_file(
                    use_cached=True, spoiler=attachment.is_spoiler()
                    )
                for attachment in attachments if not attachment.is_spoiler()
                ]
            )

    @commands.command()
    async def esnipe(self, ctx: KanaContext, target: typing.Optional[discord.TextChannel]): # type: ignore
        """
        e(dit)-Snipes the last message that was edited from the mentioned channel, or the current channel if no channel is mentioned.

        :param target: The channel to E(dit)-Snipes from.
        :type target: discord.TextChannel, optional
        """
        if not ctx.guild:
            return

        if 'snipe' in self.bot.disabled_modules.get(ctx.guild.id, []):
            return await ctx.send("Sniping is disabled in this server.")

        target: discord.TextChannel = target or ctx.channel # type: ignore
        msg = self.edit_msg.get(target.id, None)

        if not msg:
            return await ctx.send(f"There is nothing for me to esnipe {'here' if target is ctx.channel else f'in {target.mention}'}.")

        message, timestamp = msg
        embed = discord.Embed(description=message.content, timestamp=timestamp)
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Snipe(bot))
