import discord
from discord.ext import commands

import inspect
import os 

import psutil
import aiohttp
from datetime import datetime

from time import time
from .utils import time as timeutil

class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    def _get_uptime(self, breif=False):
        return timeutil.deltaconv(int(time()) - int(self.client._uptime), breif)

    @commands.command()
    async def uptime(self, ctx):
        await ctx.send(self._get_uptime())

    async def _get_commits(self, count=3):
        async with aiohttp.ClientSession() as session:
            async with session.get(url='https://api.github.com/repos/duckist/Kanapy/commits', params={"per_page": 3}) as res:
                res = await res.json()
                arr = []
                for i in res:
                    url = i["html_url"]
                    if len(i['commit']['message']) > 50:    arr.append(f"[`{i['sha'][0:6]}`]({url}) {i['commit']['message'][:50]}...")
                    else:   arr.append(f"[`{i['sha'][0:6]}`]({url}) {i['commit']['message']}")
                return "\n".join(arr)

    @commands.command()
    async def about(self, ctx):
        owner = await self.client.get_guild(659189385085845515).fetch_member(651454696208465941)

        mem = psutil.Process().memory_full_info().uss / 1024**2
        cpu = psutil.Process().cpu_percent() / psutil.cpu_count()

        embed = discord.Embed(color=discord.Color.from_rgb(54, 57, 63), description='Latest Changes:\n' + await self._get_commits(), timestamp=datetime.utcnow())
        embed.set_author(name=str(owner), icon_url=owner.avatar_url, url="https://github.com/duckist")
        embed.add_field(name="Version", value=f"discord.py-{discord.__version__}", inline=True)
        embed.add_field(name="Uptime", value=self._get_uptime(breif=True), inline=True)
        embed.add_field(name="Process", value=f'{mem: .2f} MiB\n{cpu:.2f}% CPU', inline=True)

        await ctx.send(embed=embed)
    
    @commands.command() 
    async def source(self, ctx, *, command: str = None):
        source_url = "https://github.com/duckist/Kanapy"
        if command is None:    return await ctx.send(source_url)

        obj = self.client.get_command(command.replace(".", ""))
        if obj is None:    return await ctx.send("Could not find command")

        src = obj.callback.__code__
        module = obj.callback.__module__
        filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith('discord'):
            location = os.path.relpath(filename).replace('\\', '/')
        location = module.replace('.', '/') + '.py'

        await ctx.send(f'<{source_url}/blob/main/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>')

def setup(client):
    client.add_cog(Stats(client))
