import discord
from discord.ext import commands

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["wp"])
    @commands.has_permissions(manage_messages=True)
    async def waifupurge(self, ctx, amount=30):
        if amount > 50: return await ctx.reply("Please enter a smaller number")

        def check(m):
            return (m.author.id == 432610292342587392 or m.content.startswith("$"))
            
        await ctx.channel.purge(limit=amount, check=check)
        try:    await ctx.message.add_reaction('\u2705')
        except:    pass


async def setup(bot):
    await bot.add_cog(Moderation(bot))
