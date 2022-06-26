import re

import discord
from discord.ext import commands

from ..utils.subclasses import Kana


class Events(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        await self.bot.pool.execute(
            """
        DELETE FROM prefixes WHERE id = $1
        """,
            guild.id,
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content != after.content:
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if re.fullmatch(rf"<@!?{self.bot.user.id}>", message.content):  # type: ignore
            prefixes = [
                f"`{prefix}`"
                for prefix in await self.bot.get_prefix(message)
                if not re.fullmatch(r'<@!?668118072611176470>\s?', prefix)
            ]
            await message.reply(
                f"Hello \N{WAVING HAND SIGN}, my prefix{f' is `{prefixes[0]}`!' if len(prefixes) <= 1 else 'es are ' + ', '.join(prefixes)}"
            )


async def setup(bot: Kana):
    await bot.add_cog(Events(bot))
