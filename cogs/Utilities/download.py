from difflib import get_close_matches
from glob import glob
from os import urandom
from pathlib import Path
import re
from time import perf_counter
from typing import Optional
from urllib import parse

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from jishaku.features.root_command import natural_size as ns
import yt_dlp

from ..utils import Kana, KanaContext

# these are all stolen :D
LINK_REGEX = re.compile(
    r"("
        r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$|"
        r"https?://(?P<subdomain>[^/]+\.)?reddit(?:media)?\.com/r/(?P<slug>[^/]+/comments/(?P<reddit_id>[^/?#&]+))|"
        r"https?:\/\/www\.tiktok\.com\/(?:embed|t|@(?P<user_id>[\w\.-]+)\/video)\/(?P<tiktok_id>[A-Za-z]+)|"
        r"^http(?:s)?://(?:www\.)?(?:[\w-]+?\.)?reddit.com(/r/|/user/)?(?(1)([\w:]{2,21}))(/comments/)?(?(3)(\w{5,6})(?:/[\w%\\\\-]+)?)?(?(4)/(\w{7}))?/?(\?)?(?(6)(\S+))?(\#)?(?(8)(\S+))?$|"
        r"https?://(?:(?:www|m(?:obile)?)\.)?twitter\.com/(?:(?:i/web|[^/]+)/status|statuses)/(?P<id>\d+)|"
        r"(?P<url>https?://(?:www\.)?instagram\.com(?:/[^/]+)?/(?:p|tv|reel)/(?P<insta_id>[^/?#&]+))"
    r")"
)


class LinkConverter(commands.Converter[Kana]):
    async def convert(self, ctx: KanaContext, argument: str):  # type: ignore
        argument = argument.lstrip("<").rstrip(">")

        if '-dev' in argument and await ctx.bot.is_owner(ctx.author):
            return argument

        match = LINK_REGEX.match(argument)

        if not match:
            raise commands.BadArgument(
                "No URL found, sources I support are `YouTube`, `Reddit`, `TikTok`, `Twitter` or `Instagram`."
            )

        parsed = parse.urlparse(match.group())
        if parsed.hostname and any(
            name
            for name in ["reddit.com", "redditmedia.com", "twitter.com"]
            if parsed.hostname.endswith(name)
        ):
            channel = ctx.channel
            if ctx.guild and (
                (
                    isinstance(channel, discord.Thread)
                    and (channel.parent and channel.parent.nsfw)
                )
                or (
                    hasattr(channel, "nsfw") and channel.nsfw  # type: ignore # because it doesn't understand ctx.guild check ignores rest of the attr errors
                )
            ):
                raise commands.BadArgument(
                    f"The provided source (`{parsed.hostname}`) could potentially contain NSFW, Please redo this command in an NSFW channel and/or in DMs."
                )
        return match.group()


class Download(commands.Cog):
    def __init__(self, bot: Kana):
        self.bot = bot

    def _download(self, URL: str, guild_filesize: int = 8388608) -> Optional[Path]:
        name = urandom(8).hex()

        ydl_opts = {
            "format": f'(bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo+bestaudio/best)'
                      f'[filesize<?{guild_filesize}]',
            "quiet": True,
            "merge_output_format": "mp4",
            "max_filesize": guild_filesize,
            "outtmpl": f"temp/{name}.%(ext)s",
            "format_sort": ["vcodec:h264", "ext:mp4"],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
            ydl.download(URL)  # type: ignore

        search = get_close_matches(f"temp/{name}", glob(f"temp/{name}.*"))
        return Path(search[0]) if search else None


    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    @commands.bot_has_permissions(attach_files=True)
    async def download(self, ctx: KanaContext, *, url: LinkConverter):
        """
        Downloads the provided URL and send it to the current channel, Allowed sources are `YouTube`, `Reddit`, `TikTok`, `Twitter` or `Instagram`.

        :param url: The URL to download.
        :type url: str
        """
        msg = await ctx.send("downloading...")
        limit = ctx.guild.filesize_limit if ctx.guild else 8388608

        try:
            start = perf_counter()
            out = await self.bot.loop.run_in_executor(
                None,
                self._download,
                url,
                limit,
            )
            end = perf_counter()
        except yt_dlp.utils.RegexNotFoundError: # type: ignore
            return await msg.edit(content="Invalid URL.")
        except yt_dlp.utils.DownloadError: # type: ignore
            return await msg.edit(content="Could not download file, double check the URL and try again.")

        if not out:
            return await msg.edit(content=f"File too big, i can only send `{ns(limit)}` worth of files here.") # if its not found, its safe to assume it's errored because of the file limit.
        
        try:
            await msg.edit(
                content=f"took: `{round(end - start, 2)}s`", attachments=[discord.File(out)]
            )
        finally:
            out.unlink() # boop


async def setup(bot: Kana):
    await bot.add_cog(Download(bot))

