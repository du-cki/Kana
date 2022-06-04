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
WEBSOCKET = "<a:_:963608475982774282>"
CHAT_BOX = "<:_:963608317370974240>"
POSTGRES = "<:_:963608621017608294>"

YOUTUBE = "<:_:940649600920985691>"

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

CREATE TABLE IF NOT EXISTS username_history (
    user_id BIGINT NOT NULL,
    time_changed TIMESTAMP WITH TIME ZONE NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS avatar_history (
    user_id BIGINT NOT NULL,
    time_changed TIMESTAMP WITH TIME ZONE NOT NULL,
    avatar BYTEA NOT NULL
);
"""
