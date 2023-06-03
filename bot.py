import toml
import discord

import cogs._utils.library_override # pyright: ignore[reportUnusedImport]
from cogs._utils.subclasses import Bot


with open("Config.toml") as f:
    config = toml.load(f)

bot = Bot(
    intents=discord.Intents().all(),
    case_insensitive=True,
    strip_after_prefix=True,
    config=config,
)

bot.run(
    config["Bot"]["TOKEN"],
)
