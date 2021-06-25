import logging

logger = logging.getLogger("arc_logger")
handler = logging.StreamHandler()
formatter = logging.Formatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
