import discord
from discord.ext import commands

import re
from asyncio import TimeoutError

class Filter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.IM_REGEX = re.compile(r"((?:i|l)(?:(?:'|`|‛|‘|’|′|‵)?m| am)) ([\s\S]*)") # in cases of: "im" "i'm" "i am"
        self.KYS_REGEX = re.compile(r"(kys|killyour\s?self)") # in cases of: "kys"
        self.PLAY_REGEX = re.compile(r"(?:play|played|playing)") # in cases of: "play" "played" "playing"
        self.SHUTUP_REGEX = re.compile(r"(stfu|shut\s(?:the\s)?(?:fuck\s)?up)") # in cases of: "stfu" "shut the fuck up"
        self.GOODBYE_REGEX = re.compile(r"(?:good)? ?bye") # in cases of: "good bye" "bye"
        self.TY_REGEX = re.compile(r"(?:thank you|thanks) dad") # in cases of: "thank you dad" "thanks dad"
        self.UP_REGEX = re.compile(r"[A-Z]") # find all capital letters in a string

    def _volumeCheck(self, message : str) -> bool:
        splitMsg = message.replace(" ", "")
        upCase = self.UP_REGEX.findall(splitMsg)
        return len(upCase) / len(splitMsg) >= 0.6

    def _dadcheck(self, message : str) -> bool:
        return message.author.id == 503720029456695306

    @commands.Cog.listener("on_message")
    async def _filter(self, message : discord.Message):
        if not message.author.id == 651454696208465941:
            return

        cnt = message.content.lower()
        if not message.content == "" and (
            self._volumeCheck(message.content) \
            or self.IM_REGEX.findall(cnt) \
            or self.PLAY_REGEX.findall(cnt) \
            or self.SHUTUP_REGEX.findall(cnt) \
            or self.GOODBYE_REGEX.findall(cnt) \
            or self.KYS_REGEX.findall(cnt) \
            or self.TY_REGEX.findall(cnt) \
        ):
            try:
                dmessage = await self.bot.wait_for(
                    "message", 
                    check=self._dadcheck, 
                    timeout=10.0
                )
            except TimeoutError:
                pass
            else:
                await dmessage.delete()
                await message.channel.send("suck my dick dad bot")

async def setup(bot):
    await bot.add_cog(Filter(bot))