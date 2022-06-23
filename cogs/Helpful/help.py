import discord
from discord.ext import commands

import typing

from ..utils.constants import PARAM_RE, INVIS_CHAR, FANCY_ARROW_RIGHT, NL
from ..utils.markdown import to_ansi, to_codeblock
from ..utils.subclasses import KanaContext, Kana


class Help(commands.HelpCommand):
    def format_params(self, params: typing.List[str]) -> str:
        return " ".join(
            [
                f"{f'{to_ansi(param, 34)}' if param.startswith('<') else f'{to_ansi(param, 36)}'}"
                for param in params
            ]
        )

    def humanize(self, param: str) -> str:
        return (
            param.replace("discord.", "")
            .replace("optional", "this is Optional")
            .replace("int", "number")
        )

    def check_params(self, doc_string: str) -> str:
        params = PARAM_RE.findall(doc_string)
        if not params:
            return None  # type: ignore

        return "**Arguments:**\n" + "\n".join(
            [
                f"`{param[0]}`: {self.humanize(param[2])}\n{INVIS_CHAR}{FANCY_ARROW_RIGHT} {param[1]}"
                for param in params
            ]
        )

    async def send_bot_help(self, mapping) -> None:
        await self.context.send("never\U00002122")

    async def send_command_help(self, command: commands.Command) -> None:
        self.context: KanaContext
        if self.context.predict_ansi(self.context.author):
            parameters = (
                self.format_params(command.signature.split(" "))
                if command.signature
                else ""
            )

            description = (
                to_codeblock(
                    f"\n{self.context.clean_prefix}{to_ansi(command.qualified_name, 37)} {''.join(parameters)}",
                    "ansi",
                )
                + f"\n{command.short_doc if command.short_doc else 'No description given.'}"
            )

        else:
            description = (
                to_codeblock(
                    f"{self.context.clean_prefix}{command.qualified_name} {command.signature}"
                )
                + f"\n{command.short_doc if command.short_doc else 'No description given.'}"
            )

        params = (
            self.check_params(command.callback.__doc__)
            if command.callback.__doc__
            else None
        )

        if params:
            description += "\n\n" + params

        em = discord.Embed(description=description)

        await self.context.send(embed=em)

    async def send_group_help(self, group: commands.Group) -> None:
        pref_len = len(self.context.clean_prefix)

        if self.context.predict_ansi(self.context.author):
            commands = [
                f"{INVIS_CHAR * pref_len}{to_ansi(FANCY_ARROW_RIGHT + ' ' + command.name, 37)} {self.format_params(command.signature.split(' ')) if command.signature else ''}"
                for command in group.commands
            ]
            parameters = (
                self.format_params(group.signature.split(" "))
                if group.signature
                else ""
            )

            description = (
                to_codeblock(
                    f"\n{self.context.clean_prefix}{to_ansi(group.name, 37)} {parameters}"
                    + to_ansi(f"\n{f'{NL}'.join(commands)}", 37),
                    "ansi",
                )
                + f"\n{group.short_doc if group.short_doc else 'No description given.'}"
            )

        else:
            commands = [
                f"{INVIS_CHAR * pref_len}{FANCY_ARROW_RIGHT} {command.name} {command.signature}"
                for command in group.commands
            ]

            description = (
                to_codeblock(
                    f"\n{self.context.clean_prefix}{group.name} {group.signature}"
                    f"\n{f'{NL}'.join(commands)}"
                )
                + f"\n{group.short_doc if group.short_doc else 'No description given.'}"
            )

        sub_commands = [
            f"`{command.name}`\n{INVIS_CHAR}{FANCY_ARROW_RIGHT} {command.short_doc}"
            for command in group.commands
        ]

        params = (
            self.check_params(group.command.__doc__) if group.command.__doc__ else None
        )

        if params:
            description += "\n\n" + params

        if sub_commands:
            description += (
                f"\n\nSub-Command{'s' if len(sub_commands) > 1 else ''}:\n"
                + "\n".join(sub_commands)
            )

        em = discord.Embed(description=description)
        await self.context.send(embed=em)


async def setup(bot: Kana):
    bot.help_command = Help()
