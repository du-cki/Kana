import difflib
from typing import List, Optional

import discord
from discord.ext import commands

from ..utils.markdown import to_codeblock
from ..utils.paginator import EmbeddedPaginator
from ..utils.subclasses import Kana, KanaContext


class ExtensionConverter(commands.Converter[Kana]):
    async def convert(
        self, ctx: commands.Context[Kana], argument: str
    ) -> Optional[List[str]]:
        if argument.lower() in ("all", "*", "~"):
            return list(ctx.bot.extensions)

        extension = difflib.get_close_matches(
            argument, ctx.bot.extensions.keys(), n=1, cutoff=0.4
        )
        if not extension:
            raise commands.BadArgument(f"`{argument}` is not a valid extension.")

        return extension


class Owner(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context[Kana]) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command(aliases=["del"])
    async def delete(self, ctx: KanaContext):
        """
        Deletes the message that the author replied to.
        """

        target: Optional[discord.MessageReference] = ctx.message.reference
        if target is None:
            return await ctx.send(
                "Reply to the message you want to delete", delete_after=5.0
            )

        if not isinstance(target.resolved, discord.Message):
            return

        if target.resolved.author is not ctx.me:
            return await ctx.send(
                "You can only delete messages that I sent", delete_after=5.0
            )

        await target.resolved.delete()

    @commands.command()
    async def cleanup(self, ctx: KanaContext, limit: commands.Range[int, 1, 500] = 25):
        """
        Deletes the last `limit` amount of messages sent by the bot, if the bot has the `Manage Messages` permission, then it will also delete the command messages.

        :param limit: The number of messages to delete, defaults to 50 if none specified.
        :type limit: int, optional
        """
        if ctx.guild is None or isinstance(
            ctx.channel,
            discord.DMChannel | discord.PartialMessageable | discord.GroupChannel,
        ):  # typehinting purposes
            return

        limit += 1
        bulk = ctx.channel.permissions_for(ctx.guild.me).manage_messages

        if bulk:
            prefixes = await self.bot.get_prefix(ctx.message)

        def check(message: discord.Message):
            return message.author == ctx.me or (
                bulk and any(message.content.startswith(prefix) for prefix in prefixes)
            )

        res = await ctx.channel.purge(limit=limit, bulk=bulk, check=check)
        if not res:
            return await ctx.send("No messages were found to cleanup.")

        await ctx.send(
            f'Cleaned up {len(res)} message{"s" if len(res) > 1 else ""}.',
            delete_after=10.0,
        )

    @commands.command(name="reload", aliases=["re", "rl"])
    async def _reload(self, ctx: KanaContext, *, extensions: ExtensionConverter):
        """
        Reloads the closest `Extension` it finds with the name provided.

        :param extension: The name of the extension to reload.
        :type extension: str
        """

        msg: List[str] = []
        for extension in extensions:  # type: ignore
            try:
                extension: str
                await self.bot.reload_extension(extension)
            except Exception as e:
                fmt = (
                    "\n"
                    if (msg[-1].endswith("\n") and not msg[-1].endswith("```\n"))
                    else ""
                )  # jank string formatting
                msg.append(
                    f'{fmt}\U000026a0 Could not reload `{extension}` \U000026a0 \n{to_codeblock(str(e), "py")}\n'
                )
            else:
                msg.append(f"\U0001f501 Reloaded `{extension}`\n")

        await EmbeddedPaginator(
            ctx,
            msg,
            per_page=5,
            title=f"Reloaded Extension{'s' if len(msg) > 1 else ''}",
        ).start()


async def setup(bot: Kana):
    await bot.add_cog(Owner(bot))
