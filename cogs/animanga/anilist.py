import re

from discord import Interaction, app_commands
from discord.utils import utcnow

from aiohttp import ClientSession
from datetime import timedelta

from typing import Any, Optional

from .. import logger
from .types import FetchResult, FetchRequestResult, StudioEdge, Trailer, SEARCH_TYPE, Node

SEARCH_QUERY = """
query ($search: String, $type: MediaType) {
  Page(perPage: 10) {
    media(search: $search, type: $type, sort: POPULARITY_DESC) {
      title {
        romaji
      }
    }
  }
}
"""

REMINDER_QUERY = """
query ($id: Int) {
  Media(id: $id) {
    airingSchedule {
      nodes {
        timeUntilAiring
        episode
        mediaId
      }
    }
  }
}
"""

FETCH_QUERY = """
query ($search: String, $type: MediaType) {
  Media(search: $search, type: $type) {
    title {
      romaji
    }
    coverImage {
      extraLarge
      color
    }
    trailer {
      site
      id
    }
    description(asHtml: false)
    id
    genres
    averageScore
    episodes
    duration
    chapters
    status
    bannerImage
    siteUrl
    isAdult
    airingSchedule {
      nodes {
        timeUntilAiring
        episode
        mediaId
      }
    }
    studios {
      edges {
        node {
          name
          siteUrl
        }
        isMain
      }
    }
  }
}
"""

TAG_PATTERN = re.compile(
    r'<(?P<double>(br><br)+)>|<\/?(?P<tag>(br|i|b|p)+)>|<a href="(?P<link>[^"]+)">(?P<title>[^"]+)<\/a>'
)
TAG_MAPPING = {
    "br": "\n",
    "br><br": "\n",  # merge two break lines into one, because anilist is ruthless on the break lines
    "b": "**",
    "i": "*",
    "p": "",
}
STATUS_MAPPING = {
    "FINISHED": "Finished",
    "RELEASING": "Releasing",
    "NOT_YET_RELEASED": "Not Released",
    "CANCELLED": "Cancelled",
    "HIATUS": "Hiatus",
}


def formatter(obj: re.Match[Any]) -> str:
    group = obj.groups()
    if len(group) == 2:
        # strategy: hyperlink
        return f"[{group[0]}]({group[1]})"
    # strategy: replace markup
    return TAG_MAPPING.get(group[0], "")


def parse_schedule_time(schedule: Node):
    schedule["timeUntilAiring"] = utcnow() + timedelta(  # type: ignore
        seconds=schedule["timeUntilAiring"]
    )
    return schedule

def parse_studios(edge: StudioEdge):
    name = edge.get("node", {}).get("name")
    url = edge.get("node", {}).get("siteUrl")
    return {
        "name": name,
        "url": url,
        "formatted": f"[{name}]({url})",
        "main": edge.get("isMain", False)
    }


def cleanup_html(description: str) -> str:
    return TAG_PATTERN.sub(formatter, description)


def create_trailer_url(data: Trailer) -> str:
    if data["site"] == "youtube":
        return "https://www.youtube.com/watch?v=" + data["id"]
    elif data["site"] == "dailymotion":
        return "https://www.dailymotion.com/video/" + data["id"]

    logger.error(f"Found a different trailer site, data: {data}")
    return ""


async def search(
    session: ClientSession, search: str, search_type: SEARCH_TYPE
) -> list[str]:
    """
    Searches for a Series, this won't return any information but rather titles.

    Parameteres
    ------------
    session: ClientSession
        A `aiohttp.ClientSession` object to do the request with.

    search: str
        The search query.

    search_type: SEARCH_TYPE
        An Enum of either ANIME or MANGA.
    """

    req = await session.post(
        "https://graphql.anilist.co/",
        json={
            "query": SEARCH_QUERY,
            "variables": {
                "search": search if search else None,
                "type": search_type.name,
            },
        },
    )

    resp = await req.json()
    if resp.get("errors"):
        logger.error(
            f"Search result {search!r} ({search_type.name}) yielded an error: \n{resp}"
        )
        return []

    data = resp.get("data", {}).get("Page", {}).get("media", [])

    return [result["title"]["romaji"] for result in data]


async def search_auto_complete(
    interaction: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """
    A wrapper around the `search` function for auto-completes.

    Parameteres
    ------------
    interaction: discord.Interaction
        The Interaction instance.

    current: str
        The search query.
    """

    assert (
        isinstance(interaction.command, app_commands.Command)
        and interaction.command.parent
    )

    SEARCH_TYPE_MAPPING = {
        "anime": SEARCH_TYPE.ANIME,
        "manga": SEARCH_TYPE.MANGA,
    }

    search_type = SEARCH_TYPE_MAPPING.get(interaction.command.parent.name)
    if search_type is None:
        logger.error(
            "'search_auto_complete' was called outside designated area it was designed for, Please use the function `search` instead."
        )
        return []

    results = await search(
        interaction.client.session, current, search_type  # type: ignore
    )

    # TODO: cache the results

    return [app_commands.Choice(name=result, value=result) for result in results]


async def fetch(
    session: ClientSession, search: str, search_type: SEARCH_TYPE
) -> Optional[FetchResult]:
    """
    Fetches information about a Series.

    Parameteres
    ------------
    session: ClientSession
        A `aiohttp.ClientSession` object to do the request with.

    search: str
        The search query.

    search_type: SEARCH_TYPE
        An Enum of either ANIME or MANGA.
    """

    req = await session.post(
        "https://graphql.anilist.co/",
        json={
            "query": FETCH_QUERY,
            "variables": {
                "search": search if search else None,
                "type": search_type.name,
            },
        },
    )

    resp = await req.json()
    if resp.get("errors"):
        logger.error(
            f"Fetch result {search!r} ({search_type}) yielded an error: \n{resp}"
        )
        return None

    data: Optional[FetchRequestResult] = resp.get("data", {}).get("Media")
    if not data:
        logger.error(data)
        return None

    return { # type: ignore
        **data,
        "type": search_type,
        "title": data.get("title", {}).get("romaji", "N/A"),
        "coverImage": data["coverImage"]["extraLarge"],
        "color": data["coverImage"]["color"],
        "description": cleanup_html(data["description"]),
        "status": STATUS_MAPPING.get(data["status"], data["status"]),
        "trailer": create_trailer_url(data["trailer"]) if data["trailer"] else None,
        "airingSchedule": list(map(
            parse_schedule_time, data.get("airingSchedule", {}).get("nodes", [])
        )),
        "studios": list(map(
            parse_studios, data.get("studios", {}).get("edges")
        ))
    }


async def fetch_schedules(session: ClientSession, search: int) -> Optional[list[Node]]:
    """
    Fetches schedules about an AniManga.

    Parameteres
    ------------
    session: ClientSession
        A `aiohttp.ClientSession` object to do the request with.

    search: str
        The AniList AniManga ID.
    """

    req = await session.post(
        "https://graphql.anilist.co/",
        json={
            "query": REMINDER_QUERY,
            "variables": {
                "id": search,
            },
        },
    )

    resp = await req.json()
    if resp.get("errors"):
        logger.error(f"fetch_schedules {search!r} yielded an error: \n{resp}")
        return None

    data: Optional[FetchRequestResult] = resp.get("data", {}).get("Media")
    if not data:
        return None

    return list(
        map(parse_schedule_time, data.get("airingSchedule", {}).get("nodes", []))
    )
