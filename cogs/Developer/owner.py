import discord
from discord.ext import commands

import difflib

from ..utils.markdown import to_codeblock

class ExtensionConverter(commands.Converter):
    async def convert(self, ctx, argument):
        extension = difflib.get_close_matches(argument, ctx.bot.extensions.keys(), n=1, cutoff=0.4)
        if not extension:
            raise commands.BadArgument(f"`{argument}` is not a valid extension.")
        return extension[0]

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command(aliases=['del'])
    async def delete(self, ctx: commands.Context):
        """
        Deletes the message that the author replied to.
        """

        target: discord.MessageReference = ctx.message.reference # type: ignore
        if target is None:
            return await ctx.send('Reply to the message you want to delete', delete_after=5.0)

        if target.resolved.author is not ctx.me: # type: ignore
            return await ctx.send('You can only delete messages that I sent', delete_after=5.0)

        await target.resolved.delete() # type: ignore

    @commands.command()
    @commands.guild_only()
    async def cleanup(self, ctx: commands.Context, limit: int = 50):
        """
        Deletes the last `limit` messages sent by the bot. If the bot has the `manage_messages` permission, then it will also delete the command messages.

        :param limit: The number of messages to delete, defaults to 50 if none specified.
        :type limit: int, optional
        """
        limit += 1 # To include the command message
        bulk = ctx.channel.permissions_for(ctx.me).manage_messages # type: ignore

        def pred(message: discord.Message):
            return message.author == ctx.me or (bulk and message.content.startswith(ctx.prefix)) # type: ignore

        res = await ctx.channel.purge(limit=limit, bulk=bulk, check=pred) # type: ignore
        if not res:
            return await ctx.send('No messages were found to cleanup.')
        await ctx.send(f'Cleaned up {len(res)} message{"s" if len(res) > 1 else ""}.', delete_after=10.0)

    @commands.command()
    async def reload(self, ctx: commands.Context, extension: ExtensionConverter):
        """
        Reloads the closest `Extension` it finds with the name provided.

        :param extension: The name of the extension to reload.
        :type extension: str
        """
        try:
            await self.bot.reload_extension(extension)
        except Exception as e:
            await ctx.send(f'Could not reload `{extension}`\n{to_codeblock(e)}') # type: ignore
        else:
            await ctx.send(f'Reloaded `{extension}`')


async def setup(bot):
    await bot.add_cog(Admin(bot))
