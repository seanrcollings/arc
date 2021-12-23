import logging
import sys
import typing as t
from arc.color import colorize, effects, bg
import arc.typing as at
from arc import utils


DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


_root = logging.getLogger("arc")
_app_root = logging.getLogger("arc.app")

mode_map = {
    "development": DEBUG,
    "production": WARNING,
    "test": ERROR,
}


def root_setup(mode: at.Env):
    if len(_root.handlers) == 0:
        handler = ArcStreamHandler()
        formatter = ArcFormatter("%(levelname)s%(name)s %(message)s")
        handler.setFormatter(formatter)
        _root.addHandler(handler)

    level = mode_map.get(mode, WARNING)
    _root.setLevel(level)


# Uses camelCase to follow the convetions of the logging module
def getArcLogger(name: str = None):
    """Used Internally by arc modules to obtain a
    logger that descends from the root `arc` logger
    """
    if name:
        return logging.getLogger(f"arc.{name}")

    return _root


def getAppLogger(name: str = None):
    """Get an arc application logger"""
    if name:
        return logging.getLogger(f"arc.app.{name}")

    return _app_root


class ArcFormatter(logging.Formatter):
    level_color = {
        DEBUG: bg.BLUE,
        INFO: bg.ARC_BLUE,
        WARNING: bg.rgb(204, 195, 63),
        ERROR: bg.RED,
        CRITICAL: bg.BRIGHT_RED,
    }

    def format(self, record: logging.LogRecord):
        record.message = record.getMessage()
        record.levelname = colorize(
            f" {record.levelname:^8} ",
            self.level_color[record.levelno],
            effects.BOLD,
        )
        record.name = colorize(f"{record.name:^13}", bg.GREY)
        return super().format(record)


class ArcStreamHandler(logging.StreamHandler):
    def __init__(self, stream: t.TextIO = None):
        if not stream:
            stream = sys.stderr

        super().__init__(utils.IoWrapper(stream))
