from __future__ import annotations
import itertools
import typing as t

from arc import suggest
from arc.present.ansi import colorize, fx
from arc.present.joiner import Join

if t.TYPE_CHECKING:
    from arc.context import Context
    from arc.define import Command, Param
    from arc.config import Config


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
        return f"{self.usage()}{self.message}"

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
    def __init__(self, unrecognized: list[str], command: Command = None):
        super().__init__("", command)
        self.unrecognized = unrecognized

    def fmt(self, ctx: Context) -> str:
        message = self.usage()
        message += f"Unrecognized arguments: {Join.with_space(self.unrecognized, style=ctx.config.color.highlight)}"
        message += self.__get_suggestions(self.unrecognized, ctx.config, ctx.command)
        return message

    def __get_suggestions(
        self,
        extra: list[str],
        config: Config,
        command: Command,
    ) -> str:
        message = ""

        if config.suggest.commands:
            message += self.__fmt_suggestions(
                suggest.subcommand_suggestions(extra, command, config.suggest.distance),
                "subcommand",
                config,
            )

        if config.suggest.params:
            message += self.__fmt_suggestions(
                suggest.param_suggestions(
                    extra, command.key_params, config.suggest.distance
                ),
                "option",
                config,
            )

        return message

    def __fmt_suggestions(
        self, suggestions: suggest.Suggestions, kind: str, config: Config
    ) -> str:
        message = ""

        for param_name, param_sug in suggestions.items():
            if param_sug:
                message += (
                    f"\nUnrecognized {kind} {colorize(param_name, config.color.highlight)}, "
                    f"did you mean: {Join.with_or(param_sug, style=config.color.accent)}"
                )

        return message


class ParserError(UsageError, ArgumentError):
    ...


class ValidationError(ArgumentError):
    ...


class InternalError(ArcError):
    """Errors that fire due to development / internal errors.
    These will be noted to probably be bugs in production mode"""

    def fmt(self, ctx: Context) -> str:
        message = (
            f"{colorize('ERROR:', ctx.config.color.error, fx.BOLD)} {str(self)}\n\n"
            "This is probably a bug, please report it to the maintainer"
        )

        if link := ctx.config.links.bug:
            message += f": {link}"

        return message


class CommandError(InternalError):
    ...


class ParamError(InternalError):
    def __init__(self, message, param=None):
        super().__init__(message)
        self.param = param


class TypeArgError(InternalError):
    ...
