import discord, traceback, textwrap, io, subprocess, os
from contextlib import redirect_stdout
from discord.ext import commands

class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_result = None

    @commands.command(aliases=['re'])
    @commands.is_owner()
    async def reload(self, ctx, extension):
        try:
            self.client.unload_extension(f'cogs.{extension}')
            self.client.load_extension(f'cogs.{extension}')
            await ctx.channel.send(f'Reloaded `{extension}`')
        except:
            await ctx.channel.send(f'`{extension}` does not exist')

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):

        env = {
            'client': self.client,
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

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

def setup(client):
    client.add_cog(Admin(client))
