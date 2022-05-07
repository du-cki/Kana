import discord
from discord.ext import commands

from .utils.constants import ESCAPE, PARAM_RE, INVIS_CHAR, FANCY_ARROW_RIGHT, NL


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

        return "Arguments:\n" + "\n".join([f"`{param[0]}` : {param[2]}\n{INVIS_CHAR}{FANCY_ARROW_RIGHT} {param[1]}" for param in params])


    async def send_bot_help(self, mapping):
        await self.context.send("soon\U00002122")


    async def send_command_help(self, command):
        if self.context.predict_ansi(self.context.author):
            parameters = self.format_params(
                command.signature.split(" ")) if command.signature else ""

            description = (
                "```ansi"
                f"\n{self.context.clean_prefix}{ESCAPE}[0;37m{command.qualified_name}{ESCAPE}[0m {''.join(parameters)}"
                "```"
                f"\n{command.short_doc if command.short_doc else 'No description given.'}"
            )

        else:
            description = (
                "```\n"
                f"{self.context.clean_prefix}{command.qualified_name} {command.signature}"
                "```"
                f"\n{command.short_doc if command.short_doc else 'No description given.'}"
            )

        params = self.check_params(
            command.callback.__doc__) if command.callback.__doc__ else None

        if params:
            description += "\n\n" + params

        em = discord.Embed(
            description=description,
            color=0xE59F9F
        )

        await self.context.send(embed=em)

    async def send_group_help(self, group):
        pref_len = len(self.context.clean_prefix)

        if self.context.predict_ansi(self.context.author):
            commands = [
                f"{INVIS_CHAR * pref_len}{ESCAPE}[0;37m{FANCY_ARROW_RIGHT} {command.name}{ESCAPE}[0m {self.format_params(command.signature.split(' ')) if command.signature else ''}"
                for command in group.commands
            ]

            description = (
                "```ansi"
                f"\n{self.context.clean_prefix}{ESCAPE}[0;37m{group.name}{ESCAPE}[0m"
                f"\n{ESCAPE}[0;37m{f'{NL}'.join(commands)}{ESCAPE}[0m"
                "```"
                f"\n{group.short_doc if group.short_doc else 'No description given.'}"
            )

        else:
            commands = [
                f"{INVIS_CHAR * pref_len}{FANCY_ARROW_RIGHT} {command.name} {command.signature}"
                for command in group.commands
            ]

            description = (
                "```"
                f"\n{self.context.clean_prefix}{group.name}"
                f"\n{f'{NL}'.join(commands)}"
                "```"
                f"\n{group.short_doc if group.short_doc else 'No description given.'}"
            )

        params = [
            f"`{command.name}`\n{INVIS_CHAR}{FANCY_ARROW_RIGHT} {command.short_doc}"
            for command in group.commands
        ]

        if params:
            description += "\n\nSub-Commands:\n" + "\n".join(params)

        em = discord.Embed(
            description=description,
            color=0xE59F9F
        )

        await self.context.send(embed=em)


async def setup(bot):
    bot.help_command = Help()
