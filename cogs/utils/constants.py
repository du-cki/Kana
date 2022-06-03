import typing
import re

# random constants
FANCY_ARROW_RIGHT = "\U00002570"
ESCAPE = "\u001b"
INVIS_CHAR = "\u2800"
NL = "\n"
VALID_EDIT_KWARGS: typing.Dict[str, typing.Any] = {
    'content': None,
    'embed': None,
    'attachments': [],
    'delete_after': None,
    'allowed_mentions': None,
    'view': None,
}

# emotes
WEBSOCKET = "<a:websocket:963608475982774282>"
CHAT_BOX = "<:message:963608317370974240>"
POSTGRES = "<:postgresql:963608621017608294>"

YOUTUBE = "<:youtube_logo:940649600920985691>"

# regexes
PARAM_RE = re.compile(
    r":param (?P<param>[a-zA-Z0-9_]+):? (?P<param_description>[a-zA-Z0-9_ .,]+)"
    r"\n? +:type [a-zA-Z0-9_]+:? (?P<type>[a-zA-Z0-9_ .,]+)"
)

# sql
STARTUP_QUERY = """
CREATE TABLE IF NOT EXISTS prefixes (
    id BIGINT PRIMARY KEY,
    prefix TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    unix_time BIGINT,
    name TEXT
);

CREATE TABLE IF NOT EXISTS avatars (
    id BIGINT PRIMARY KEY,
    unix_time BIGINT,
    avatar BYTEA
);
"""
