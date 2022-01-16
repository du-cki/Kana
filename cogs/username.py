import discord
from discord.ext import commands
from .utils import db

import aiohttp

from os import environ
from dotenv import load_dotenv
load_dotenv()

db = db.MongoConnnection(environ["USER_MONGO"], "main", "r.py")

class Username(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.group(aliases=["users", "user", "usernames"], invoke_without_command=True)
    async def username(self, ctx):
        query = db.get({"_id": ctx.author.id})
        if query is None:
            return await ctx.send("I have no usernames recorded from you")
        _users = list(query.values())
        await ctx.channel.send(f'Your username(s): `{", ".join(_users[2])}`')

    @username.command()
    async def add(self, ctx, username: str):
        if any(c in "!@#$%^&*()-+?=,<>/" for c in username):    return await ctx.send("There are no special characters in usernames dummy") # returns when string has special characters

        _user = await self._checkUser(username)
        if _user is None:   return await ctx.send("This username does not exist") # returns when the username does not exist
        
        if db.get({"robloxUser": username}) is not None:    return await ctx.send("Someone has already claimed this username") # returns when someone already has that username in the database

        q = db.get({"_id": ctx.author.id})
        if q is not None: # if author is already in the database, run this
            if len(q['robloxUser']) > 5:    return await ctx.send("You have reached your max limit for usernames (5)")

            db.update({"_id": ctx.author.id}, {"$push": {"robloxUser": _user}})
            db.update({"_id": ctx.author.id}, {"$set": {"username": str(ctx.author)}})
            return await ctx.send(f"Added `{_user}` to my database")
        
        db.insert({"_id": ctx.author.id, "username": str(ctx.author), "robloxUser": [_user]})
        await ctx.send(f"Added `{_user}` to my database")

    async def _checkUser(self, username):
        async with aiohttp.ClientSession() as session:
            async with session.get(url='https://users.roblox.com/v1/users/search', params={"keyword": username}) as res:
                r = await res.json()
                try:
                    return r["data"][0]["name"]
                except KeyError:
                    return None
                except Exception as e:
                    print(e)

    @username.command(aliases=["delete", "del", "rem"])
    async def remove(self, ctx, username):
        q = db.get({"_id": ctx.author.id, "robloxUser": username})
        if q is None:
            return await ctx.send(f"You don't have any entries named `{username}`")
        res = db.update({"_id": ctx.message.author.id}, {"$pull": {"robloxUser": username}})

        if res["robloxUser"] == [username]:
            db.delete({"_id": ctx.author.id})

        await ctx.send(f"Removed `{username}`")
    
def setup(client):
    client.add_cog(Username(client))
