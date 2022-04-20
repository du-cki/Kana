import re

# random constants
FANCY_ARROW_RIGHT = "\U00002570"
ESCAPE = "\u001b"
INVIS_CHAR = "\u2800"


# emotes
WEBSOCKET = "<a:websocket:963608475982774282>"
CHAT_BOX = "<:message:963608317370974240>"
POSTGRES = "<:postgresql:963608621017608294>"


# regexes
PARAM_RE = re.compile(
    r":param (?P<param>[a-zA-Z0-9_]+):? (?P<param_description>[a-zA-Z0-9_ .,]+)"
    r"\n? +:type [a-zA-Z0-9_]+:? (?P<type>[a-zA-Z0-9_ .,]+)"
)