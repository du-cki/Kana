import discord, traceback, textwrap, io, subprocess, os
from contextlib import redirect_stdout
from discord.ext import commands

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    @commands.command(aliases=['re'])
    @commands.is_owner()
    async def reload(self, ctx, extension):
        try:
            self.bot.unload_extension(f'cogs.{extension}')
            self.bot.load_extension(f'cogs.{extension}')
            await ctx.channel.send(f'Reloaded `{extension}`')
        except:
            await ctx.channel.send(f'`{extension}` does not exist')

    @commands.command(aliases=["wp"])
    @commands.has_permissions(manage_messages=True)
    async def waifupurge(self, ctx, amount=30):
        if amount > 50: return await ctx.reply("Please enter a smaller number")

        def check(m):
            return (m.author.id == 432610292342587392 or m.content.startswith("$"))
        await ctx.channel.purge(limit=amount, check=check)
        try:
            await ctx.message.add_reaction('\u2705')
        except:
            pass

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

def setup(bot):
    bot.add_cog(Admin(bot))
