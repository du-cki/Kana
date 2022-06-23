import typing
import re

# random constants
FANCY_ARROW_RIGHT = "\U00002570"
ESCAPE = "\u001b"
INVIS_CHAR = "\u2800"
NL = "\n"
VALID_EDIT_KWARGS: typing.Dict[str, typing.Any] = {
    "content": None,
    "embed": None,
    "attachments": [],
    "delete_after": None,
    "allowed_mentions": None,
    "view": None,
}

# emotes
WEBSOCKET = "<a:_:963608475982774282>"
CHAT_BOX = "<:_:963608317370974240>"
POSTGRES = "<:_:963608621017608294>"

YOUTUBE = "<:_:940649600920985691>"

DOUBLE_LEFT = "<:_:982445997269606450>"
LEFT = "<:_:982445470548893696>"
RIGHT = "<:_:982444215936118784>"
DOUBLE_RIGHT = "<:_:982379739165655060>"

# regexes
PARAM_RE = re.compile(
    r":param (?P<param>[a-zA-Z0-9_]+):? (?P<param_description>[a-zA-Z0-9_ .,]+)"
    r"\n? +:type [a-zA-Z0-9_]+:? (?P<type>[a-zA-Z0-9_ .,]+)"
)

# jank parsers
with open("schema.sql", "r") as f:
    STARTUP_QUERY = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

library_versions: typing.Dict[str, str] = {}

for module in requirements:
    match = re.findall(
        r"https:\/\/github.com\/(?P<user_name>[a-zA-Z0-9_.-]+)\/(?P<project>[a-zA-Z0-9_.-]+)@(?P<commit_hash>[a-zA-Z0-9_.-]+)",
        module,
    )
    if match:
        _, project, commit_hash = match[0]
        library_versions[project] = commit_hash
