from __future__ import annotations
import typing as t

from arc.present.ansi import colorize
from arc.present.joiner import Join


if t.TYPE_CHECKING:
    from arc.context import Context
    from arc.define import Command, Param


class Exit(SystemExit):
    def __init__(self, code: int = 0, message: str | None = None) -> None:
        super().__init__(code)
        self.message = message

    def fmt(self, ctx: Context):
        return self.message


class ArcError(Exception):
    def fmt(self, ctx: Context):
        return str(self)


class ExternalError(ArcError):
    """Errors that fire due to user / input errors"""


class ExecutionError(ExternalError):
    ...


class ArgumentError(ExternalError):
    """Error with the value of a provided argument"""


class ConversionError(ArgumentError):
    """Raised if a type conversion fails"""

    def __init__(self, value, message: str, details=None):
        self.value = value
        self.details = details
        super().__init__(message)


class UsageError(ExternalError):
    """Indicates that the command was used incorrectly.
    If a command is provided, the command's usage will be printed,
    along with the provided error message"""

    def __init__(self, message: str, command: Command = None):
        self.message = message
        self.command = command

    def fmt(self, ctx: Context):
        if self.command:
            usage = self.command.doc.usage()
            return f"{usage}\n{self.message}"

        return self.message

    def usage(self) -> str:
        if self.command:
            return self.command.doc.usage() + "\n"

        return ""


class InvalidParamValueError(UsageError, ArgumentError):
    def __init__(
        self, message: str, param: Param, detail: str = None, command: Command = None
    ):
        super().__init__(message, command)
        self.param = param
        self.detail = detail

    def fmt(self, ctx: Context) -> str:
        name = colorize(self.param.cli_name, ctx.config.color.highlight)
        string = f"{self.usage()}invalid value for {name}: {self.message}"

        if self.detail:
            string += " "
            string += colorize(f"({self.detail})", ctx.config.color.subtle)

        return string


class MissingArgValueError(UsageError, ArgumentError):
    def __init__(self, params: list[Param], command: Command = None):
        super().__init__("", command)
        self.params = params

    def fmt(self, ctx: Context) -> str:
        params = Join.with_comma(
            (param.cli_name for param in self.params), style=ctx.config.color.highlight
        )
        return f"{self.usage()}The following arguments are required: {params}"


class MissingOptionValueError(UsageError, ArgumentError):
    def __init__(self, param: Param, command: Command = None):
        super().__init__("", command)
        self.param = param

    def fmt(self, ctx: Context) -> str:
        name = colorize(self.param.cli_name, ctx.config.color.highlight)
        return f"{self.usage()}option {name} expected 1 argument"


class UnrecognizedArgError(UsageError, ArgumentError):
    ...


class ParserError(UsageError, ArgumentError):
    ...


class ValidationError(ArgumentError):
    ...


class InternalError(ArcError):
    """Errors that fire due to development / internal errors"""


class CommandError(InternalError):
    ...


class ParamError(InternalError):
    def __init__(self, message, param=None):
        super().__init__(message)
        self.param = param


class TypeArgError(InternalError):
    ...
