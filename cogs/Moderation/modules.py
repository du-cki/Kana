import discord
from discord.ext import commands

from ..utils.subclasses import Kana, KanaContext

class Modules(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot
        self.modules = {
            "snipe": "Lets users 'snipe' the last message that got deleted within the last 2 minutes in a channel.",
            }

    @commands.group(aliases=['config', "configs", "modules"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def module(self, ctx: KanaContext):
        """
        Configure modules.
        """
        await ctx.send_help(ctx.command)

    @module.command(name="list", aliases=["all"])
    async def _list(self, ctx: KanaContext):
        """
        Lists all modules and their current status in the server.
        """
        if not ctx.guild:
            return
        
        WHITE_CHECK_MARK = "\u2705"
        CROSS_EMOJI = "\u274C"

        desc = ''
        for module, description in self.modules.items():
            desc += f"\n{WHITE_CHECK_MARK if module not in self.bot.disabled_modules.get(ctx.guild.id, []) else CROSS_EMOJI} {module}: {description}"

        embed = discord.Embed(title="Modules", description=desc)
        await ctx.send(embed=embed)
    
    @module.command(aliases=["on"])
    async def enable(self, ctx: KanaContext, module: str):
        """
        Enables a module in the server.

        :param module: The name of the module to enable.
        :type module: str
        """
        if not ctx.guild:
            return

        module = module.lower()
        if module not in self.modules:
            return await ctx.send(f"Module `{module}` does not exist.")

        if module not in self.bot.disabled_modules.get(ctx.guild.id, []):
            return await ctx.send(f"Module `{module}` is already enabled.")

        q = """
        UPDATE guild_settings
        SET disabled_modules = ARRAY_REMOVE(disabled_modules, $1)
        WHERE guild_id = $2
        RETURNING disabled_modules;
        """
        disabled_modules = await self.bot.pool.fetchval(q, module, ctx.guild.id)
        self.bot.disabled_modules[ctx.guild.id] = disabled_modules
        await ctx.send(f"Module `{module}` has been enabled.")

    @module.command(aliases=["off"])
    async def disable(self, ctx: KanaContext, module: str):
        """
        Disables a module in the server.
            
        :param module: The name of the module to disable.
        :type module: str
        """
        if not ctx.guild:
            return
        
        module = module.lower()
        if module not in self.modules:
            return await ctx.send(f"Module `{module}` does not exist.")

        if module in self.bot.disabled_modules.get(ctx.guild.id, []):
            return await ctx.send(f"Module `{module}` is already disabled.")

        q = """
        UPDATE guild_settings
        SET disabled_modules = ARRAY_APPEND(disabled_modules, $1)
        WHERE guild_id = $2
        RETURNING disabled_modules;
        """
        disabled_modules = await self.bot.pool.fetchval(q, module, ctx.guild.id)
        self.bot.disabled_modules[ctx.guild.id] = disabled_modules
        await ctx.send(f"Module `{module}` has been disabled.")

async def setup(bot):
    await bot.add_cog(Modules(bot))
