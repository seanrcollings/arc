from __future__ import annotations
import typing as t

from arc import logging, utils
from arc.color import colorize, fg
from arc.result import Result

if t.TYPE_CHECKING:
    from arc.command.param import Param
    from arc.execution_state import ExecutionState

logger = logging.getArcLogger("arg")


class Argument:
    """Represents an argument passed in from the command line.
    Can be thought of as an "instance" of a param
    """

    __slots__ = ("value", "param")

    def __init__(self, value: t.Any, param: Param):
        self.value = value
        self.param = param

    def __repr__(self):
        return f"Argument(value={self.value}, param={self.param!r})"

    @property
    def name(self):
        return self.param.arg_name

    def log(self, message: str, *args):
        logger.info("%s: " + message, colorize(self.name, fg.YELLOW), *args)

    def pre_execute(self, _state: ExecutionState):
        if utils.is_context_manager(self.value):
            self.log("opening resource")
            self.value.__enter__()

    def post_execute(self, result: Result, _state: ExecutionState):
        if utils.is_context_manager(self.value):
            self.log("closing resource")
            args: tuple = (None, None, None)
            if result.err:
                exc = result.unwrap()
                args = (type(exc), exc, exc.__traceback__)

            self.value.__exit__(*args)
