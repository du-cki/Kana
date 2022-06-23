import discord
from discord.ext import commands

import re
from asyncio import TimeoutError

from ..utils.subclasses import Kana


class Filter(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot
        self.MASTER_REGEX = re.compile(
            r"((?:i|l)(?:(?:'|`|‛|‘|’|′|‵)?m| am)) ([\s\S]*)"
            r"|(kys|killyour\s?self)"
            r"|(?:play|played|playing)"
            r"|(stfu|shut\s(?:the\s)?(?:fuck\s)?up)"
            r"|(?:good)? ?bye"
            r"|(?:thank you|thanks) dad"
        )  # in case of: "i'm", "kys", "play", "stfu", "good bye", "thanks dad"
        self.UP_REGEX = re.compile(r"[A-Z]")  # find all capital letters in a string

    def _volumeCheck(self, message: str) -> bool:
        splitMsg = message.replace(" ", "")
        upCase = self.UP_REGEX.findall(splitMsg)
        return len(upCase) / len(splitMsg) >= 0.6

    @commands.Cog.listener("on_message")
    async def _filter(self, message: discord.Message):
        if not message.author.id == 651454696208465941:
            return

        cnt = message.content.lower()
        if (
            not message.content == ""
            and self._volumeCheck(message.content)
            or self.MASTER_REGEX.findall(cnt)
        ):
            try:

                def _dadcheck(message: discord.Message) -> bool:
                    return (
                        message.author.id == 503720029456695306
                        and message.channel.id == message.channel.id
                    )

                dmessage = await self.bot.wait_for(
                    "message", check=_dadcheck, timeout=10.0
                )

            except TimeoutError:
                pass
            else:
                await dmessage.delete()
                await message.channel.send("suck my dick dad bot")


async def setup(bot: Kana):
    await bot.add_cog(Filter(bot))
