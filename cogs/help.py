import discord
from discord.ext import commands

import re

ESCAPE = "\u001b"
PARAM_RE = re.compile(
    r":param (?P<param>[a-zA-Z0-9_]+):? (?P<param_description>[a-zA-Z0-9_ .,]+)"
    r"\n? +:type [a-zA-Z0-9_]+:? (?P<type>[a-zA-Z0-9_ .,]+)"
)

class Help(commands.HelpCommand):

    def format_params(self, params: list) -> list:
        return " ".join(
            [
                f"{f'<{ESCAPE}[0;34m{param[1:-1]}{ESCAPE}[0m>' if param.startswith('<') else f'[{ESCAPE}[0;36m{param[1:-1]}{ESCAPE}[0m]'}"
                for param in params
            ]
        )

    def check_params(self, doc_string: str) -> str:
        params = PARAM_RE.findall(doc_string)
        if not params:
            return None
        
        return "Arguments:\n" + "\n".join([f"`{param[0]}` : {param[2]}\n\u2800\U00002570\u2800{param[1]}" for param in params])

    async def send_bot_help(self, mapping):
        await self.context.send("soon\U00002122")

    async def send_command_help(self, command):
        if self.context.determine_ansi(self.context.author):
            parameters = self.format_params(command.signature.split(" ")) if command.signature else ""

            description = (
                f"```ansi"
                f"\n{self.context.clean_prefix}{ESCAPE}[0;37m{command.qualified_name}{ESCAPE}[0m {''.join(parameters)}"
                f"```"
                f"\n{command.short_doc if command.short_doc else 'No description given.'}"
            )

        else:
            description = (
                "```\n"
                f"{self.context.clean_prefix}{command.qualified_name} {command.signature}"
                "```"
                f"\n{command.short_doc if command.short_doc else 'No description given.'}"
            )
        
        params = self.check_params(command.callback.__doc__) if command.callback.__doc__ else None
        
        if params:
            description += "\n\n" + params

        em = discord.Embed(
            description=description,
            color=0x2F3136
        )

        await self.context.send(embed=em)

    async def send_group_help(self, group):
        await self.context.send("soon\U00002122")


async def setup(bot):
    bot.help_command = Help()
