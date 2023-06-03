# -*- mode: snippet -*-
# name: Cog Template
# description: A yasnippet for a basic Cog template.
# expand-env: ((yas-indent-line 'fixed))
# key: !cog
# --

import discord
from discord.ext import commands

class ${1:`(capitalize (file-name-nondirectory (file-name-sans-extension (buffer-file-name))))`}(commands.Cog):
    ...$2

async def setup(bot: commands.Bot):
    await bot.add_cog($1(bot))
