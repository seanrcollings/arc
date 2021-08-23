import enum
import inspect
from dataclasses import dataclass
from typing import Any, NewType, Optional

from arc import errors
from arc.utils import symbol

# TODO: handle Context as a hidden arg

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
    def __init__(self, parameter: inspect.Parameter, meta: Meta):
        self.paramater: inspect.Parameter = parameter
        self.arg_name: str = parameter.name
        self.arg_alias: str = meta.name or parameter.name
        self.annotation: type = parameter.annotation
        self.default: Any = parameter.default
        self.hidden = meta.hidden
        self.short = meta.short
        if self.short and len(self.short) > 1:
            raise errors.ArgumentError(
                f"Argument {self.arg_name}'s shortened name is longer than 1 character"
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
                self.type = ParamType.POS
            elif parameter.kind is parameter.KEYWORD_ONLY:
                self.type = ParamType.KEY
            elif parameter.kind is parameter.POSITIONAL_OR_KEYWORD:
                if self.default is NO_DEFAULT:
                    self.type = ParamType.POS
                else:
                    self.type = ParamType.KEY

    def __repr__(self):
        type_name = getattr(self.annotation, "__name__", None)
        if not type_name:
            type_name = self.annotation

        return f"<Param {self.arg_name}({self.type}): {type_name} = {self.default}>"

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
