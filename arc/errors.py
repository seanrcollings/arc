from __future__ import annotations
from typing import TYPE_CHECKING

from arc import color


if TYPE_CHECKING:
    from arc.command.param import Param
    from arc.execution_state import ExecutionState


class ArcError(Exception):
    """Base Arc Exception"""

    def __init__(self, *args):
        super().__init__()
        self.message = " ".join(args)

    def __str__(self):
        return self.message


class ExecutionError(ArcError):
    """Raised if there is a problem during the execution of a command"""


class CommandError(ArcError):
    """Raised when there is an error in the creation of a command"""


class ValidationError(ArcError):
    """Raised when there is an error in validating command input or in a validator callback"""


class ActionError(ArcError):
    """Raised when a action callback fails to execute"""


class TokenizerError(ArcError):
    def __init__(self, token, mode):
        self.token = token
        super().__init__(f"Unable to understand: `{self.token}` in command string")


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
    def __init__(self, message: str, param: Param, state: ExecutionState):
        arg = color.colorize(param.cli_rep(), color.fg.ARC_BLUE)
        super().__init__(f"Invalid value for {arg}: {message}")
        self.param = param
        self.state = state


class ConversionError(ArgumentError):
    """Raised if a type conversion fails """

    def __init__(self, value, message: str, source=None):
        self.value = value
        self.source = source
        super().__init__(message)
