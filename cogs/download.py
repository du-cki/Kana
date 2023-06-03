import discord
from discord.ext import commands

from jishaku.features.root_command import natural_size as ns

import re
import yt_dlp # pyright: ignore[reportMissingTypeStubs] # stubs when
import asyncio

from yt_dlp.extractor.pinterest import PinterestIE # pyright: ignore[reportMissingTypeStubs]

from pathlib import Path
from time import perf_counter

from . import BaseCog

from typing import TYPE_CHECKING, Any, Optional, Annotated

if TYPE_CHECKING:
    from ._utils.subclasses import Bot, Context

# fmt: off
SOURCE_REGEX = re.compile(
    r"("
        r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$|" # https://stackoverflow.com/a/37704433
        r"https?:\/\/(?P<subdomain>[^/]+\.)?reddit(?:media)?\.com\/r\/(?P<slug>[^/]+\/comments\/(?P<reddit_id>[^\/?#&]+))|"
        r"https?:\/\/(?:m|www|vm)\.tiktok\.com\/\S*?\b(?:(?:(?:usr|v|embed|user|video)\/|\?shareId=|\&item_id=)(\d+)|(?=\w{7})(\w*?[A-Z\d]\w*)(?=\s|\/$))\b|"
        r"https?://(?:(?:www|m(?:obile)?)\.)?twitter\.com/(?:(?:i/web|[^/]+)/status|statuses)/(?P<twitter_id>\d+)|"
        r"(?P<url>https?://(?:www\.)?instagram\.com(?:/[^/]+)?/(?:p|tv|reel)/(?P<insta_id>[^/?#&]+))"
        f"{PinterestIE._VALID_URL[4:]}" # to satisfy python. # pyright: ignore[reportPrivateUsage]
    r")",
    re.IGNORECASE | re.MULTILINE
)
# fmt: on

class FileTooLarge(Exception):
    def __init__(self, limit: int, message: discord.Message, *args: object) -> None:
        super().__init__(*args)
        self.limit = limit
        self.original_message = message


class LinkConverter(commands.Converter["Bot"]):
    async def convert(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, ctx: "Context", argument: str
    ):
        if "-dev" in ctx.message.content and await ctx.bot.is_owner(ctx.author):
            return argument.lstrip("-dev").rstrip("-dev").lstrip("<").rstrip(">")

        argument = argument.lstrip("<").rstrip(">")

        match = SOURCE_REGEX.match(argument)

        if not match:
            raise commands.BadArgument(
                "No URL found, sources I support are `YouTube`, `Reddit`, `TikTok`, `Twitter`, `Instagram` or `Pinterest`."
            )

        return match.group()


def fs_filter(limit: int):
    def inner(info: dict[str, Any], **kwargs: Any):
        max_fs = info.get("max_filesize")
        if max_fs and max_fs > limit:
            return "The video is too big"

        fs_approx = info.get("filesize_approx")
        if fs_approx and fs_approx > limit:
            return "The video is too big"

    return inner


class Download(BaseCog):
    def __init__(self, bot: "Bot") -> None:
        super().__init__(bot)
        self.DOWNLOAD_PATH = self.CONFIG["PATH_TO_DOWNLOAD"]

    def _download(
        self,
        URL: str,
        *,
        max_filesize: int = (25 * 1024 * 1024),
    ) -> Optional[Path]:
        ydl_opts = {
            "quiet": not self.bot.config["Bot"]["IS_DEV"],
            "outtmpl": self.DOWNLOAD_PATH + "%(id)s.%(ext)s",
            "merge_output_format": "mp4",
            "max_filesize": max_filesize,
            "format_sort": ["vcodec:h264"],
            "format": f"(bestvideo+bestaudio/best)[filesize<?{max_filesize}]",
            # "match_filter": fs_filter(max_filesize), # clips dont go well with this.
        }

        with yt_dlp.YoutubeDL(  # pyright: ignore[reportUnknownMemberType]
            ydl_opts
        ) as ydl:  # pyright: ignore[reportUnknownVariableType]
            info: dict[str, Any] = ydl.extract_info(URL)  # type: ignore

        path = Path(f"{self.DOWNLOAD_PATH}{info['id']}.{info['ext']}")
        if path.exists():
            if path.stat().st_size > max_filesize:
                path.unlink(missing_ok=True)
                return None

            return path

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    @commands.bot_has_permissions(attach_files=True)
    async def download(
        self,
        ctx: "Context",
        *,
        url: Annotated[str, LinkConverter],
    ):
        """
        Downloads the provided URL and send it to the current channel,
        Allowed sources are `YouTube`, `Reddit`, `TikTok`, `Twitter` or `Instagram`.

        Parameters
        -----------
        url: str
            The URL to download.
        """
        msg = await ctx.send("downloading...")

        limit = ctx.guild.filesize_limit if ctx.guild else (25 * 1024 * 1024)

        try:
            start = perf_counter()
            path = await asyncio.to_thread(self._download, url, max_filesize=limit)
            end = perf_counter()
        except yt_dlp.utils.DownloadError:  # pyright: ignore[reportUnknownMemberType]
            return await msg.edit(
                content="Could not download the URL. Double check the URL and try again."
            )

        if not path:
            raise FileTooLarge(
                limit, msg
            )  # if its not found, its safe to assume it's errored because of the file limit.

        try:
            await msg.edit(
                content=f"took: `{round(end - start, 2)}s`",
                attachments=[discord.File(path)],
            )
        except discord.HTTPException as err:
            if (
                err.code == 40005
            ):  # if discord somehow still doesn't like my 8MB files (happens alot), i'd like to let the user know.
                raise FileTooLarge(limit, msg)

            raise err
        finally:
            path.unlink(missing_ok=True)  # boop

    @download.error
    async def download_error(self, ctx: "Context", error: commands.CommandError):
        error = getattr(error, "original", error)

        if isinstance(error, FileTooLarge):
            return await error.original_message.edit(
                content=f"Sorry, the file is too large to upload. I can only send `{ns(error.limit)}` worth of files here."
            )

        raise error


async def setup(bot: "Bot"):
    await bot.add_cog(Download(bot))
