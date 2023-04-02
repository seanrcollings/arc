import logging

from arc.color import bg, colorize, fg, fx

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


class ArcFormatter(logging.Formatter):
    level_color = {
        DEBUG: bg.BLUE,
        INFO: bg.ARC_BLUE,
        WARNING: bg.rgb(204, 195, 63),
        ERROR: bg.RED,
        CRITICAL: bg.BRIGHT_RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        record.levelname = colorize(
            f" {record.levelname:^8} ",
            self.level_color[record.levelno],
            fx.BOLD,
            fg.BLACK,
        )
        record.name = colorize(f"{record.name:^5}", bg.GREY)
        return super().format(record)


mode_map = {
    "development": INFO,
    "production": WARNING,
    "test": ERROR,
}


logger = logging.getLogger("arc")
logger.setLevel(ERROR)
handler = logging.StreamHandler()
formatter = ArcFormatter("%(levelname)s%(name)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
