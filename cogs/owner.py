import discord
from discord.ext import commands
from discord import app_commands

from contextlib import redirect_stdout
import traceback, textwrap, io, subprocess, os

from typing import Literal

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    @commands.command(aliases=['re'])
    @commands.is_owner()
    async def reload(self, ctx, extension):
        try:
            await self.bot.unload_extension(f'cogs.{extension}')
            await self.bot.load_extension(f'cogs.{extension}')
            await ctx.channel.send(f'Reloaded `{extension}`')
        except discord.ext.commands.errors.ExtensionNotLoaded:
            await ctx.channel.send(f'`{extension}` does not exist')

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Sync'd tree")

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            try:
              if ret is None:
                  if value:
                      await ctx.send(f'```py\n{value}\n```')
              else:
                  self._last_result = ret
                  await ctx.send(f'```py\n{value}{ret}\n```')
            except discord.errors.HTTPException:
              
              if len(value) == 0:   return await ctx.send("No output")

              buffer = io.BytesIO(value.encode('utf-8'))
              await ctx.send(file=discord.File(buffer, filename='output.txt'))

async def setup(bot):
    await bot.add_cog(Admin(bot))
