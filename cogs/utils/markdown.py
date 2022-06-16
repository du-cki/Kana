def to_ansi(string: str, color: int) -> str:
    """
    Returns the given string into the given color (in reality, a color code) in ANSI.
    """
    return f"\033[{color}m" + string + "\033[0m"


def to_codeblock(code: str, lang: str = "") -> str:
    """
    Returns the given code in a codeblock with the given language.
    """
    return f"```{lang}\n{code}\n```"
