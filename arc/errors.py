from __future__ import annotations
from typing import TYPE_CHECKING

from arc import color


if TYPE_CHECKING:
    from arc.command.param import Param
    from arc.context import Context


class ArcError(Exception):
    """Base Arc Exception"""


class ExecutionError(ArcError):
    """Raised if there is a problem during the execution of a command"""


class CommandError(ArcError):
    """Raised when there is an error in the creation of a command"""


class ValidationError(ArcError):
    """Raised when there is an error in validating command input or in a validator callback"""


class ParserError(ArcError):
    """Raised when there is an error parsing the arguments"""


class ArgumentError(ArcError):
    """Raised when an error occurs to the scope of a single argument"""


class MissingParamType(ArgumentError):
    ...


class MissingArgError(ArgumentError):
    def __init__(self, message: str, **data):
        super().__init__(message)
        self.data = data


class InvalidParamaterError(ArgumentError):
    def __init__(self, message: str, param: Param, ctx: Context):
        arg = color.colorize(param.cli_rep(), color.fg.ARC_BLUE)
        super().__init__(f"Invalid value for {arg}: {message}")
        self.param = param
        self.ctx = ctx


class ConversionError(ArgumentError):
    """Raised if a type conversion fails """

    def __init__(self, value, message: str, source=None):
        self.value = value
        self.source = source
        super().__init__(message)


class UsageError(ArcError):
    """Indicates that the command was used incorrectly"""

    def __init__(self, message: str, ctx: Context = None):
        self.message = message
        self.ctx = ctx

    def __str__(self):
        usage = self.ctx.command.get_usage(self.ctx, help_hint=False)
        return f"{usage}\n{self.message}"


class Exit(Exception):
    """Instructs arc to exit with `code`"""

    def __init__(self, code: int):
        self.code = code
        super().__init__(str(code))
