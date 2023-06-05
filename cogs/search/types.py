from typing import Optional, TypedDict


class Artist(TypedDict):
    name: str
    url: str
    is_verified: Optional[bool]


class Album(TypedDict):
    name: str
    url: str
    artist: list[Artist]

class AccessToken(TypedDict):
    clientId: str
    accessToken: str
    accessTokenExpirationTimestampMs: int
    isAnonymous: bool

class Song(TypedDict):
    track_name: str
    track_url: str
    album: Album
    artists: list[Artist]


class Owner(TypedDict):
    username: str
    display_name: str
    url: str


class Playlist(TypedDict):
    name: str
    url: str
    description: str
    owner: Optional[Owner]
