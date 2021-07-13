import logging
from arc.color import fg, effects, colorize


logger = logging.getLogger("arc_logger")


def indent(string: str, distance="\t", split="\n"):
    """Indents the block of text provided by the distance"""
    return f"{distance}" + f"{split}{distance}".join(string.split(split))


def header(contents: str):
    logger.debug(colorize(f"{contents:^35}", effects.UNDERLINE, effects.BOLD, fg.BLUE))
