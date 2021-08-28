import enum
import inspect
from dataclasses import dataclass
from typing import Any, NewType, Optional

from arc import errors
from arc.color import fg, colorize
from arc.utils import symbol
from arc.config import config


NO_DEFAULT = symbol("NO_DEFAULT")
VarPositional = NewType("VarPositional", list)
VarKeyword = NewType("VarKeyword", dict)


class ParamType(enum.Enum):
    POS = "positional"
    KEY = "keyword"
    FLAG = "flag"
    SPECIAL = "special"


@dataclass
class Meta:
    name: Optional[str] = None
    type: Optional[ParamType] = None
    short: Optional[str] = None
    hidden: bool = False
    default: Any = NO_DEFAULT


class Param:
    """Represetns a single function arguments

    Instance Variables:
        paramater (inspect.Paramater): The Paramater object generated
            for the associated function argument. Usually not needed as
            the other values should provide all context needed. But we
            store it off just in case.
        arg_name (str): The actual name of the argument of the function.
            can be used to pass some value to said function
        arg_alias (str): The name to be used to pass a value to
            the argument from the command line. Will default to the
            `arg_name` if no other value is provided
        annotation (type): The type of the argument
        default (Any): Default value for the argument
        hidden (bool): Whether or not the value is visible to the
            command  line. Usually used to hide `Context` arguments
        short (str): the single-character shortened name for the
            argument on the command line
    """

    def __init__(self, parameter: inspect.Parameter, meta: Meta):
        self.paramater: inspect.Parameter = parameter
        self.arg_name: str = parameter.name
        self.annotation: type = parameter.annotation
        self.default: Any = parameter.default
        self.hidden: bool = meta.hidden
        self.short: Optional[str] = meta.short

        if self.short and len(self.short) > 1:
            raise errors.ArgumentError(
                f"Argument {self.arg_name}'s shortened name is longer than 1 character"
            )

        # By default, snake_case args are transformed to kebab-case
        # for the command line. However, this can be ignored
        # by declaring an explicit name in the Meta()
        # or by setting the config value to false
        if meta.name:
            self.arg_alias: str = meta.name
        else:
            self.arg_alias = (
                parameter.name.replace("_", "-")
                if config.tranform_snake_case
                else parameter.name
            )

        if self.annotation in (VarPositional, VarKeyword):
            self.hidden = True

        if meta.default is not NO_DEFAULT or self.default is parameter.empty:
            self.default = meta.default

        if self.annotation in (VarPositional, VarKeyword):
            self.type: ParamType = ParamType.SPECIAL
        elif meta.type:
            self.type = meta.type
        else:
            if parameter.annotation is bool:
                self.type = ParamType.FLAG
                if self.default is NO_DEFAULT:
                    self.default = False
            elif parameter.kind is parameter.POSITIONAL_ONLY:
                raise errors.ArgumentError(
                    "Positional onyl arguments are not allowed as arc "
                    "passes all arguments by keyword internally"
                    f"please remove the {colorize('/', fg.YELLOW)} from",
                    "your function definition",
                )
            elif parameter.kind is parameter.KEYWORD_ONLY:
                self.type = ParamType.KEY
            elif parameter.kind is parameter.POSITIONAL_OR_KEYWORD:
                self.type = ParamType.POS
                # if parameter.default is parameter.empty:
                #     self.type = ParamType.POS
                # else:
                #     self.type = ParamType.KEY

    def __repr__(self):
        type_name = getattr(self.annotation, "__name__", self.annotation)

        return f"<Param {self.arg_name}({self.type}): {type_name} = {self.default}>"

    def __format__(self, spec: str):
        modifiers = spec.split("|")
        name = self.arg_alias

        if self.is_positional:
            formatted = f"<{name}>"
        else:
            if "short" in modifiers:
                assert self.short
                name = self.short
                denoter = config.short_flag_denoter
            else:
                denoter = config.flag_denoter

            formatted = f"{denoter}{name}"

            if "usage" in modifiers:
                if self.is_keyword:
                    formatted += " <...>"

        if self.optional:
            formatted = f"[{formatted}]"

        return formatted

    @property
    def optional(self):
        return self.default is not NO_DEFAULT

    @property
    def is_keyword(self):
        return self.type is ParamType.KEY

    @property
    def is_positional(self):
        return self.type is ParamType.POS

    @property
    def is_flag(self):
        return self.type is ParamType.FLAG
