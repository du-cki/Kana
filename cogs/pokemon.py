from __future__ import annotations

import discord
from discord.ext import commands

import time
import re
import io
import csv

from typing import TYPE_CHECKING

from . import BaseCog

if TYPE_CHECKING:
    from typing_extensions import Self
    from typing import Optional

    from . import Bot, Context


POKETWO_ID = 716390085896962058
HINT_RE = re.compile("The pokémon is (?P<hint>.*).")
CATCH_RE = re.compile(
    "Congratulations <@!?(?P<catcher>[0-9]+)>! You caught a level (?P<level>[0-9]{1,2}) (?P<name>[a-zA-Zé. ]+)!(?: Added to Pokédex. You received (?P<reward>[0-9]+) Pokécoins!)?"
)


class Hint:
    def __init__(self, hint: str):
        self.hint = list(hint)

    def add(self, guess: Self):
        hint = str(guess)
        assert len(self.hint) == len(hint), "hint must've changed, length changed."

        for idx, letter in enumerate(hint):
            if self.hint[idx] == "_" and self.hint[idx] != letter:
                self.hint[idx] = letter

    def __str__(self):
        return "".join(self.hint)


class Pokemon(BaseCog):
    def __init__(self, bot: "Bot") -> None:
        super().__init__(bot)
        self.pokemon_table: dict[str, dict[str, str]] = {}
        self.active_spawns: dict[int, Optional[Hint]] = {}
        self.flags = {
            # "en": "\U0001f1ec\U0001f1e7",
            "ja": "\U0001f1ef\U0001f1f5",
            "ja_r": "\U0001f1ef\U0001f1f5",
            "ja_t": "\U0001f1ef\U0001f1f5",
            "de": "\U0001f1e9\U0001f1ea",
            "fr": "\U0001f1eb\U0001f1f7",
        }

    async def build_pokemon_table(self):
        async with self.bot.session.get(
            "https://raw.githubusercontent.com/poketwo/data/master/csv/pokemon.csv"
        ) as req:
            raw_csv = await req.text()
            reader = csv.reader(io.StringIO(raw_csv))

            final = {}
            for row in reader:
                ja, ja_r, ja_t, en, de, fr = (
                    row[11],
                    row[12],
                    row[13],
                    row[14],
                    row[16],
                    row[17],
                )

                final[en] = {"ja": ja, "ja_r": ja_r, "ja_t": ja_t, "de": de, "fr": fr}

            assert final["name.en"] == {
                "ja": "name.ja",
                "ja_r": "name.ja_r",
                "ja_t": "name.ja_t",
                "de": "name.de",
                "fr": "name.fr",
            }
            self.pokemon_table = final

    async def cog_load(self) -> None:
        await self.build_pokemon_table()

    def guess(self, guess: Hint) -> list[str]:
        hint = str(guess)
        if not self.pokemon_table:
            raise Exception("lookup table not ready yet.")

        guesses: list[str] = [
            p for p in self.pokemon_table.keys() if len(hint) == len(p)
        ]

        for i, letter in enumerate(hint):
            if letter != "_":
                guesses = [p for p in guesses if p[i].lower() == letter.lower()]

        return guesses

    def extract_hint(self, input: str) -> Optional[Hint]:
        match = HINT_RE.fullmatch(input)
        if not match:
            return None

        return Hint(match.groups()[0].replace("\\", ""))

    @commands.group(name="guess", aliases=["hint"], invoke_without_command=True)
    @commands.guild_only()
    async def _guess(self, ctx: "Context"):
        """
        Gives an estimating prediction from a `PokéTwo` hint.
        """
        if not self.pokemon_table:
            raise commands.BadArgument(
                "Pokémon table not build yet, please give me a few seconds."
            )

        hint = None
        if ctx.message.reference:
            msg = ctx.message.reference.resolved
            assert isinstance(msg, discord.Message)

            if not (self.bot.is_dev or msg.author.id == POKETWO_ID):
                return await ctx.send("Please reply to a **PokéTwo** hint.")

            hint = self.extract_hint(msg.content)
        elif self.active_spawns.get(ctx.channel.id):
            hint = self.active_spawns[ctx.channel.id]

        if not hint:
            return await ctx.send(
                f'Reply to a **PokéTwo** hint whilst using this command, or run "**<@{POKETWO_ID}> hint**" and I\'ll start slowly compiling a guess from the hints.'
            )

        guesses = self.guess(hint)
        if not guesses:
            return await ctx.send("Could not make a guess.")

        if len(guesses) > 1:
            await ctx.send(
                f"I've narrowed it down to these `{len(guesses)}` guesses:\n"
                + ", ".join(f"\U0001f1ec\U0001f1e7 **{guess}**" for guess in guesses)
            )
        else:
            formatted: dict[str, str] = {
                self.flags[k]: v for k, v in self.pokemon_table[guesses[0]].items()
            }

            await ctx.send(
                f"\U0001f1ec\U0001f1e7 **{guesses[0]}**, "
                + ", ".join(  # so the english name is always first.
                    f"{k} **{v}**" for k, v in formatted.items() if v
                )
            )

    @_guess.command(hidden=True)
    @commands.is_owner()
    async def rebuild(self, ctx: "Context"):
        """
        Rebuilds internal `PokéTwo` data table.
        """
        msg = await ctx.send("rebuilding cache...")
        start = time.perf_counter()
        await self.build_pokemon_table()
        end = time.perf_counter()

        await msg.edit(content=f"rebuilt cache (took: `{end - start:.2}s`)")

    @commands.Cog.listener("on_message")
    async def poketwo_spawns(self, message: discord.Message):
        if message.author.id != POKETWO_ID:
            return

        await self.check_poketwo_catch(message)
        await self.check_poketwo_spawn(message)
        await self.check_poketwo_hints(message)

    async def check_poketwo_hints(self, message: discord.Message):
        hint = self.extract_hint(message.content)
        if not hint:
            return

        active = self.active_spawns.get(message.channel.id)
        if active:
            return active.add(hint)

        self.active_spawns[message.channel.id] = hint

    async def check_poketwo_spawn(self, message: discord.Message):
        if not message.embeds:
            return

        if message.embeds[0].title != "A wild pokémon has appeared!":
            return

        self.active_spawns[message.channel.id] = None

    async def check_poketwo_catch(self, message: discord.Message):
        match = CATCH_RE.fullmatch(message.content)
        if not match:
            return

        if message.channel.id in self.active_spawns:
            self.active_spawns.pop(message.channel.id)


async def setup(bot: "Bot"):
    await bot.add_cog(Pokemon(bot))
