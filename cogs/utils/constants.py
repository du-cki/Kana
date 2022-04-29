import re

# random constants
FANCY_ARROW_RIGHT = "\U00002570"
ESCAPE = "\u001b"
INVIS_CHAR = "\u2800"
NL = "\n"

# emotes
WEBSOCKET = "<a:websocket:963608475982774282>"
CHAT_BOX = "<:message:963608317370974240>"
POSTGRES = "<:postgresql:963608621017608294>"

YOUTUBE = "<:youtube_logo:940649600920985691>"

# sql
MAIN = """
CREATE TABLE IF NOT EXISTS prefixes (
id BIGINT PRIMARY KEY,
prefix TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
id BIGINT,
unix_time BIGINT,
name TEXT
);

CREATE TABLE IF NOT EXISTS avatars (
id BIGINT,
unix_time BIGINT,
avatar BYTEA
);
"""

# regexes
PARAM_RE = re.compile(
    r":param (?P<param>[a-zA-Z0-9_]+):? (?P<param_description>[a-zA-Z0-9_ .,]+)"
    r"\n? +:type [a-zA-Z0-9_]+:? (?P<type>[a-zA-Z0-9_ .,]+)"
)