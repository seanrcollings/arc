from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    from arc.context import Context


class Exit(SystemExit):
    ...


class ArcError(Exception):
    ...


class ExternalError(ArcError):
    """Errors that fire due to user / input errors"""


class ArgumentError(ExternalError):
    ...


class ConversionError(ArgumentError):
    """Raised if a type conversion fails"""

    def __init__(self, value, message: str, source=None):
        self.value = value
        self.source = source
        super().__init__(message)


class UsageError(ExternalError):
    """Indicates that the command was used incorrectly.
    If a ctx is provided, the command's usage will be printed,
    along with the provided error message"""

    def __init__(self, message: str, ctx: Context = None):
        self.message = message
        self.ctx = ctx

    def __str__(self):
        if self.ctx:
            usage = self.ctx.command.get_usage(self.ctx, help_hint=False)
            return f"{usage}\n{self.message}"

        return self.message


class MissingArgError(UsageError):
    ...


class UnrecognizedArgError(UsageError):
    ...


class InternalError(ArcError):
    """Errors that fire due to development / internal errors"""


class ParamError(InternalError):
    def __init__(self, message, param):
        super().__init__(message)
        self.param = param
