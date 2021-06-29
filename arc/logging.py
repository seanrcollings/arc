import logging
from arc.color import fg, effects


class ArcFormatter(logging.Formatter):
    prefixes = {
        logging.INFO: f"{fg.BLUE}🛈{effects.CLEAR} ",
        logging.WARNING: f"{fg.YELLOW}{effects.BOLD}WARNING{effects.CLEAR}: ",
        logging.ERROR: f"{fg.RED}{effects.BOLD}ERROR{effects.CLEAR}: ",
    }

    def format(self, record: logging.LogRecord):
        prefix = self.prefixes.get(record.levelno, "")
        record.msg = prefix + str(record.msg)
        return super().format(record)


logger = logging.getLogger("arc_logger")
handler = logging.StreamHandler()
formatter = ArcFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
