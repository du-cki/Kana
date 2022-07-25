import discord
from discord.ext import commands

import csv
import re
import time

from io import StringIO
from typing import List, Dict

from ..utils import Kana, KanaContext


class Pokemon(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot
        self.HINT_REGEX = re.compile(r'The pokémon is (?P<pokemon>[^"]+).')
        self.flags = {
            "en": "\U0001f1ec\U0001f1e7",
            "ja": "\U0001f1ef\U0001f1f5",
            "ja_r": "\U0001f1ef\U0001f1f5",
            "ja_t": "\U0001f1ef\U0001f1f5",
            "de": "\U0001f1e9\U0001f1ea",
            "fr": "\U0001f1eb\U0001f1f7",
        }

    @commands.group(invoke_without_command=True)
    async def hint(self, ctx: KanaContext):
        """
        Gets a hint for a pokétwo spawn.
        """
        message = ctx.message.reference

        if not message:
            return await ctx.send("You're not replying to any hints.")

        message = message.resolved

        if isinstance(message, discord.DeletedReferencedMessage | None):  # linter
            return

        match = self.HINT_REGEX.fullmatch(message.content)
        if not match:
            return await ctx.send("No matches found.")

        if not hasattr(self, "pokemons"):
            await ctx.invoke(self.refresh)

        hint = match.group("pokemon").replace("\\_", "_")
        guesses = await self.guess(hint)

        if len(guesses) > 1:
            guesses = "\n".join(f"**{guesses}**")
            return await ctx.send(
                f"Multiple guesses found:\n{guesses}"
            )

        pokemon = self.pokemons.get(guesses[0])

        if not pokemon:
            return  # linter

        pokemon["en"] = guesses[0] # as its the key, i can't do much about this.

        names = pokemon.items()
        formatted: Dict[str, str] = {
            self.flags[k]: v
            for k, v in names
        }

        await ctx.send(
            ', '.join(f"{k} **{v}**" for k, v in formatted.items())
        )

    @hint.command(aliases=["build"])
    @commands.is_owner()
    async def refresh(self, ctx: KanaContext):
        """
        Refreshes the hint pokémon cache.
        """
        if hasattr(self, "pokemons"):
            del self.pokemons

        message = await ctx.send("building pokémon cache, give me second.")
        start = time.perf_counter()
        await self.build_pokemon_lookup_dict()

        await message.edit(
            content=f"done building cache, and it took `{time.perf_counter() - start:.2f}` seconds."
        )

    async def build_pokemon_lookup_dict(self) -> None:
        raw_csv = await (
            await self.bot.session.get(
                "https://raw.githubusercontent.com/poketwo/data/master/csv/pokemon.csv"
            )
        ).text()
        reader = csv.reader(StringIO(raw_csv))

        final = {}
        for row in reader:
            ja, ja_r, ja_t, en, de, fr = (
                row[9],
                row[10],
                row[11],
                row[12],
                row[14],
                row[15],
            )

            final[en] = {"ja": ja, "ja_r": ja_r, "ja_t": ja_t, "de": de, "fr": fr}

        self.pokemons: Dict[str, Dict[str, str]] = final

    async def guess(self, hint: str) -> List[str]:
        if not hasattr(self, "pokemons"):
            await self.build_pokemon_lookup_dict()

        guesses: List[str] = [
            pokemon for pokemon in self.pokemons.keys() if len(hint) == len(pokemon)
        ]  # this reduces the number of guesses to a reasonable amount.

        for i, letter in enumerate(hint):
            if letter == "_":
                continue

            guesses = [
                pokemon for pokemon in guesses if pokemon[i].lower() == letter.lower()
            ]

        return guesses


async def setup(bot: Kana):
    await bot.add_cog(Pokemon(bot))
