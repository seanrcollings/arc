import logging
import functools
import traceback
import sys

from arc import config
from arc.result import Err

logger = logging.getLogger("arc_logger")

NO_OP = Err("NoOp")


def no_op():
    return NO_OP


class handle:
    def __init__(self, *exceptions: type[Exception], exit_code: int = 1):
        self.exceptions = exceptions
        self.exit_code = exit_code

    def __call__(self, func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return inner

    def __enter__(self):
        yield self

    def __exit__(self, exc_type, exc_value, trace):
        # Rebubble an exit call
        if exc_type is SystemExit:
            return False

        if config.mode == "development":
            return False

        if exc_type:
            logger.debug(format_exception(exc_value))
            logger.error(exc_value)
            sys.exit(self.exit_code)


def format_exception(e: BaseException):
    return "".join(
        traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
    )
