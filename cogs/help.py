import discord
from discord.ext import commands

ESCAPE = "\u001b"


class Help(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        await self.context.send("soon\U00002122")

    async def send_command_help(self, command):
        if self.context.author.is_on_mobile():
            description = f"""
            ```\n{self.context.clean_prefix}{command.qualified_name} {command.signature}```\n{command.short_doc}
            """
        else:
            parameters = [
                f"{f' <{ESCAPE}[0;34m{param[1:-1]}{ESCAPE}[0m>' if param.startswith('<') else f' [{ESCAPE}[0;36m{param[1:-1]}{ESCAPE}[0m]'}"
                for param in command.signature.split(" ")
            ]
            description = f"""
            ```ansi\n{self.context.clean_prefix}\u001b[0;37m{command.qualified_name}\u001b[0m{''.join(parameters)}```\n{command.short_doc}
            """

        em = discord.Embed(
            description=description,
            color=0x2F3136
        )
        await self.context.send(embed=em)

    async def send_group_help(self, group):
        await self.context.send("soon\U00002122")


async def setup(bot):
    bot.help_command = Help()
