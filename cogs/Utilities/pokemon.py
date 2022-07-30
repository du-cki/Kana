import discord
from discord.ext import commands

import csv
import re
import time

from PIL import Image
from torch import cuda
from typing import List, Dict
from cachetools import LRUCache
from io import StringIO, BytesIO
from transformers import ViTForImageClassification, ViTFeatureExtractor  # type: ignore

from ..utils import Kana, KanaContext


class Pokemon(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot
        self.device = "cuda" if cuda.is_available() else "cpu"
        self.spawn_cache: LRUCache[int, discord.Message] = LRUCache(1000)
        self.HINT_REGEX = re.compile(r'The pokémon is (?P<pokemon>[^"]+).')
        self.CATCH_REGEX = re.compile(
            r"Congratulations <@!?(?P<catcher>[0-9]+)>! You caught a level (?P<pokemon_level>[0-9]{1,2}) (?P<pokemon>[a-zA-Zé. ]+)!"
        )
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
        Tries to guess a pokétwo spawn.
        """
        message = ctx.message.reference
        spawn = self.spawn_cache.get(ctx.channel.id, None)
        if (
            spawn and spawn.embeds[0].image.url
        ) and not message:  # second expression is purely for linter.
            raw = await (await self.bot.session.get(spawn.embeds[0].image.url)).read()
            guess = await self.bot.loop.run_in_executor(
                None, self.guess_from_image, BytesIO(raw)
            )
            names = await self.get_aliases(guess)
            return await ctx.send(names, reference=spawn)

        if not message:
            return await ctx.send(
                "I don't see any active spawns, Could you specify a spawn by replying to the message?"
            )

        message = message.resolved

        if isinstance(message, discord.DeletedReferencedMessage | None):
            return

        if message.author.id != 716390085896962058 and not message.embeds:
            return await ctx.send("Please reply to a p2 spawn.")

        embed = message.embeds[0]
        if embed.title and not self.validate_p2_spawn(embed) or not embed.image.url:
            return await ctx.send("Please reply to a p2 spawn.")

        raw = await (await self.bot.session.get(embed.image.url)).read()
        guess = await self.bot.loop.run_in_executor(
            None, self.guess_from_image, BytesIO(raw)
        )
        names = await self.get_aliases(guess)
        await ctx.send(names)

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

    async def get_aliases(self, name: str) -> str:
        name = name.title()
        if not hasattr(self, "pokemons"):
            await self.build_pokemon_lookup_dict()

        pokemon = self.pokemons.get(name)

        if not pokemon:
            return "No results"  # linter

        pokemon["en"] = name
        names = pokemon.items()
        formatted: Dict[str, str] = {self.flags[k]: v for k, v in names}
        return ", ".join(f"{k} **{v}**" for k, v in formatted.items() if v)

    def prep_model(self) -> None:
        self.model = ViTForImageClassification.from_pretrained(  # type: ignore
            "imjeffhi/pokemon_classifier"
        ).to(
            self.device
        )  # type: ignore
        self.feature_extractor = ViTFeatureExtractor.from_pretrained(  # type: ignore
            "imjeffhi/pokemon_classifier"
        )

    def guess_from_image(self, image: BytesIO) -> str:
        if not hasattr(self, "model") or not hasattr(self, "feature_extractor"):
            self.prep_model()

        img = Image.open(image)
        extracted = self.feature_extractor(images=img, return_tensors="pt").to(  # type: ignore
            self.device
        )
        predicted_id = self.model(**extracted).logits.argmax(-1).item()  # type: ignore
        predicted_pokemon = self.model.config.id2label[predicted_id]  # type: ignore
        return predicted_pokemon  # type: ignore

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

    def validate_p2_spawn(self, embed: discord.Embed) -> bool:
        return bool(
            embed.title
            and "wild pokémon has appeared!" in embed.title
            and embed.description
            == "Guess the pokémon and type `pcatch <pokémon>` to catch it!"
        )

    @commands.Cog.listener("on_message")
    async def spawn(self, message: discord.Message):
        if message.author.id != 716390085896962058:
            return

        if not message.embeds:
            return

        embed = message.embeds[0]
        if embed.title and self.validate_p2_spawn(embed):
            self.spawn_cache[message.channel.id] = message

    @commands.Cog.listener("on_message")
    async def catch(self, message: discord.Message):
        if message.author.id != 716390085896962058:
            return

        match = self.CATCH_REGEX.search(message.content)
        if match:
            self.spawn_cache.pop(message.channel.id, None)
            catcher, pokemon_level, pokemon = match.groups()
            print(
                f"{catcher} caught a level {pokemon_level} {pokemon}!"
            )  # no particular reason.


async def setup(bot: Kana):
    await bot.add_cog(Pokemon(bot))
