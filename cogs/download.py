import random
import discord
from discord.ext import commands

import re
import asyncio

import yt_dlp  # pyright: ignore[reportMissingTypeStubs] # stubs when

# fmt: off
from yt_dlp.extractor.youtube import YoutubeIE, YoutubeClipIE     # pyright: ignore[reportMissingTypeStubs]
from yt_dlp.extractor.pinterest import PinterestIE                # pyright: ignore[reportMissingTypeStubs]
from yt_dlp.extractor.twitter import TwitterIE                    # pyright: ignore[reportMissingTypeStubs]
from yt_dlp.extractor.instagram import InstagramIE                # pyright: ignore[reportMissingTypeStubs]
from yt_dlp.extractor.tiktok import TikTokIE                      # pyright: ignore[reportMissingTypeStubs]
from yt_dlp.extractor.reddit import RedditIE                      # pyright: ignore[reportMissingTypeStubs]
from yt_dlp.extractor.twitch import TwitchClipsIE                 # pyright: ignore[reportMissingTypeStubs]
# fmt: on

from pathlib import Path
from time import perf_counter

from . import BaseCog

from typing import TYPE_CHECKING, Any, Optional, Annotated

if TYPE_CHECKING:
    from ._utils.subclasses import Bot, Context

DEFAULT_UPLOAD_LIMIT = 25 * 1024 * 1024


class Source:
    def __init__(self, sources: list[str] = []):
        self.sources: list[str] = []

        # this is an internal counter, as I'm re-using the regexes from yt-dlp,
        # which could cause conflicts for the same IDs, so I'll be replacing it with
        # this counter, this won't affect anything so its fine.
        self.__counter = 0
        self._flags: set[str] = set()

        for source in sources:
            self.add_source(source)

    def __str__(self):
        return rf"(?{''.join(self._flags)})^({'|'.join(self.sources)})"

    def __increment_and_return(self, _: re.Match[str]) -> str:
        self.__counter += 1

        return f"?P<id_{self.__counter}>"

    def __remove_flag(self, match: re.Match[str]) -> str:
        data = match.groupdict()
        self._flags.update(set(data["flags"]))
        return ""

    def add_source(self, source: str) -> None:
        src = re.sub(
            r"\?P\<[a-zA-Z_0-9]+\>",  # change IDs
            self.__increment_and_return,
            source.replace("/", r"\/"),
        )

        src = re.sub(
            r"\(\?(?P<flags>[a-z]+)\)\^?",  # take away the flags and put it in a set.
            self.__remove_flag,
            src,
        )

        self.sources.append(src)

    def match(self, other: str) -> Optional[re.Match[str]]:
        return re.match(
            str(self),
            other,
        )


# fmt: off
sources = Source(
    [
        YoutubeIE._VALID_URL,      # pyright: ignore[reportPrivateUsage]
        YoutubeClipIE._VALID_URL,  # pyright: ignore[reportPrivateUsage]
        TwitterIE._VALID_URL,      # pyright: ignore[reportPrivateUsage]
        PinterestIE._VALID_URL,    # pyright: ignore[reportPrivateUsage]
        TikTokIE._VALID_URL,       # pyright: ignore[reportPrivateUsage]
        InstagramIE._VALID_URL,    # pyright: ignore[reportPrivateUsage]
        RedditIE._VALID_URL,       # pyright: ignore[reportPrivateUsage]
        TwitchClipsIE._VALID_URL,  # pyright: ignore[reportPrivateUsage]
    ]
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

        match = sources.match(argument)

        if not match:
            raise commands.BadArgument(
                "No URL found, sources I support are `YouTube`, `Reddit`, `TikTok`, `Twitter`, `Instagram`, `Twitch` or `Pinterest`."
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
        max_filesize: int = DEFAULT_UPLOAD_LIMIT,
    ) -> Optional[Path]:
        _id = random.randint(0, 1000)

        ydl_opts = {
            "quiet": not self.bot.config["Bot"]["IS_DEV"],
            "outtmpl": self.DOWNLOAD_PATH + f"{_id}_%(id)s.%(ext)s",
            "merge_output_format": "mp4",
            "max_filesize": max_filesize,
            "format_sort": ["vcodec:h264"],
            "format": f"(bestvideo+bestaudio/best)[filesize<?{max_filesize}]",
            "match_filter": fs_filter(max_filesize), # clips dont go well with this.
        }

        with yt_dlp.YoutubeDL(  # pyright: ignore[reportUnknownMemberType]
            ydl_opts
        ) as ydl:
            info: dict[str, Any] = ydl.extract_info(URL)  # type: ignore

        path = Path(f"{self.DOWNLOAD_PATH}{_id}_{info['id']}.{info['ext']}")
        if path.exists():
            if path.stat().st_size < max_filesize:
                return path

            path.unlink(missing_ok=True)

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
        Downloads the provided video and send it to the current channel,
        Allowed sources are `YouTube`, `Reddit`, `TikTok`, `Twitter`, `Pinterest`, `Twitch` or `Instagram`.

        Parameters
        -----------
        url: str
            The video to download.
        """
        msg = await ctx.send("downloading...")

        limit = ctx.guild.filesize_limit if ctx.guild else DEFAULT_UPLOAD_LIMIT

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
            ):  # if discord somehow still doesn't like my 25MB files, i'd like to let the user know.
                raise FileTooLarge(limit, msg)

            raise err
        finally:
            path.unlink(missing_ok=True)  # boop


async def setup(bot: "Bot"):
    await bot.add_cog(Download(bot))
