import discord
from discord.ext import commands

from contextlib import suppress
from motor.motor_asyncio import AsyncIOMotorClient

import typing

from ..utils import Kana, KanaContext


class Username(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot
        self.db: AsyncIOMotorClient = self.bot.mongo.main["r.py"]

    @commands.group(aliases=["users", "user", "usernames"], invoke_without_command=True)
    async def username(self, ctx: KanaContext):
        """
        Gets all your usernames in the database.
        """

        query = await self.db.find_one({"_id": ctx.author.id})
        if query is None:
            return await ctx.send("I have no usernames recorded from you")

        em = discord.Embed(description="\n".join(query["robloxUser"]))
        await ctx.send(embed=em)

    @username.command()
    async def add(self, ctx: KanaContext, username: str):
        """
        Adds a username to the database.

        :param username: The username to add.
        :type username: str
        """

        if any(c in "!@#$%^&*()-+?=,<>/" for c in username):
            return await ctx.send(
                "There are no special characters in usernames dummy"
            )  # returns when string has special characters

        _user = await self._checkUser(username)
        if _user is None:
            return await ctx.send(
                "This username does not exist"
            )  # returns when the username does not exist

        if await self.db.find_one({"robloxUser": username}) is not None:
            return await ctx.send(
                "Someone has already claimed this username"
            )  # returns when someone already has that username in the database

        q = await self.db.find_one({"_id": ctx.author.id})
        if q is not None:  # if author is already in the database, run this
            if len(q["robloxUser"]) >= 5:
                return await ctx.send(
                    "You have reached your max limit for usernames (5)"
                )

            await self.db.update_one(
                {"_id": ctx.author.id}, {"$push": {"robloxUser": _user}}
            )
            await self.db.update_one(
                {"_id": ctx.author.id}, {"$set": {"username": str(ctx.author)}}
            )  # for my reference
            return await ctx.send(f"Added `{_user}` to my database")

        await self.db.insert_one(
            {"_id": ctx.author.id, "robloxUser": [_user], "username": str(ctx.author)}
        )
        await ctx.send(f"Added `{_user}` to my database")

    async def _checkUser(self, username: str) -> typing.Optional[str]:
        async with self.bot.session.get(
            url="https://users.roblox.com/v1/users/search", params={"keyword": username}
        ) as res:
            res = await res.json()
            with suppress(KeyError):
                return res["data"][0]["name"]
            return None

    @username.command(aliases=["delete", "del", "rem"])
    async def remove(self, ctx: KanaContext, username: str):
        """
        Remove a username from the database.

        :param username: The username to remove.
        :type username: str
        """

        q = await self.db.find_one({"_id": ctx.author.id, "robloxUser": username})
        if q is None:
            return await ctx.send(f"You don't have any entries named `{username}`")
        await self.db.update_one(
            {"_id": ctx.author.id}, {"$pull": {"robloxUser": username}}
        )

        q["robloxUser"].remove(username)
        if not q["robloxUser"]:
            await self.db.delete_one({"_id": ctx.author.id})

        await ctx.send(f"Removed `{username}` from my database.")


async def setup(bot: Kana):
    await bot.add_cog(Username(bot))
