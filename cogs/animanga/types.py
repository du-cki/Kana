from datetime import datetime
from typing import TypedDict, Literal, Optional

from enum import Enum


class SEARCH_TYPE(Enum):
    ANIME = 1
    MANGA = 2


class StudioNode(TypedDict):
    name: str
    siteUrl: str


class StudioEdge(TypedDict):
    node: StudioNode
    isMain: bool


class RawStudios(TypedDict):
    edges: list[StudioEdge]

class Studios(TypedDict):
    name: str
    url: str
    formatted: str
    main: bool

class Trailer(TypedDict):
    site: Literal["youtube", "dailymotion"]
    id: str


class CoverImage(TypedDict):
    extraLarge: str
    color: str


class Node(TypedDict):
    timeUntilAiring: int
    episode: int
    mediaId: int


class ParsedNode(TypedDict):
    timeUntilAiring: datetime
    episode: int
    mediaId: int


class AiringSchedule(TypedDict):
    nodes: list[Node]


class FetchRequestResult(TypedDict):
    id: int
    title: dict[Literal["romaji"], str]
    coverImage: CoverImage
    trailer: Optional[Trailer]
    description: str
    genres: list[str]
    averageScore: int
    episodes: Optional[int]
    duration: Optional[int]
    chapters: Optional[int]
    status: Literal["FINISHED", "RELEASING", "NOT_YET_RELEASED", "CANCELLED", "HIATUS"]
    bannerImage: str
    siteUrl: str
    isAdult: bool
    airingSchedule: AiringSchedule
    studios: RawStudios


class FetchResult(TypedDict):
    id: int
    averageScore: int
    bannerImage: Optional[str]
    chapters: Optional[int]
    color: str
    coverImage: str
    description: str
    episodes: Optional[int]
    duration: Optional[int]
    genres: list[str]
    isAdult: bool
    siteUrl: str
    status: str
    title: str
    trailer: Optional[str]
    airingSchedule: list[ParsedNode]
    type: SEARCH_TYPE
    studios: list[Studios]
