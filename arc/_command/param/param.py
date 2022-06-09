from __future__ import annotations
from dataclasses import dataclass
import enum
from functools import cached_property
import typing as t

from arc import errors, utils
import arc.typing as at
from arc.constants import MISSING, MissingType

if t.TYPE_CHECKING:
    from arc.context import Context


T = t.TypeVar("T")


@dataclass
class TypeInfo(t.Generic[T]):
    original_type: at.Annotation
    origin: type[T]
    sub_types: tuple[TypeInfo, ...]
    annotations: tuple[t.Any, ...]
    _name: str | None = None

    @property
    def name(self) -> str:
        return (
            self._name
            or getattr(self.origin, "name", None)
            or getattr(self.origin, "__name__", None)
            or str(self.origin)
        )

    @property
    def is_optional_type(self) -> bool:
        """The type is `Optional[T]`"""
        return (
            self.origin is t.Union
            and len(self.sub_types) == 2
            and self.sub_types[-1].original_type is type(None)
        )

    @classmethod
    def analyze(cls, annotation) -> TypeInfo:
        original_type = annotation
        origin = t.get_origin(annotation) or annotation
        annotated_args: tuple = tuple()

        if origin is t.Annotated:
            args = t.get_args(annotation)
            annotation = args[0]
            origin = t.get_origin(annotation) or annotation
            annotated_args = args[1:]

        sub_types = tuple(cls.analyze(arg) for arg in t.get_args(annotation))

        return cls(
            original_type=original_type,
            origin=origin,
            sub_types=sub_types,
            annotations=annotated_args,
        )


class Action(enum.Enum):
    STORE = "store"
    STORE_TRUE = "store_true"
    STORE_FALSE = "store_false"
    APPEND = "append"
    COUNT = "count"


class Param(
    t.Generic[T],
    utils.Display,
    members=["argument_name", "annotation"],
):
    argument_name: str
    param_name: str
    short_name: str | None
    type: TypeInfo
    default: T | MissingType | None
    description: str | None
    envvar: str | None
    prompt: str | None

    def __init__(
        self,
        argument_name: str,
        annotation: at.Annotation,
        default: T | None | MissingType = MISSING,
        param_name: str | None = None,
        short_name: str | None = None,
        description: str | None = None,
        callback: t.Callable | None = None,
        envvar: str | None = None,
        prompt: str | None = None,
    ):
        self.argument_name = argument_name
        self.param_name = param_name or argument_name
        self.short_name = short_name
        self.type = TypeInfo.analyze(annotation)
        self.default = default
        self.description = description
        self.callback = callback
        self.envvar = envvar
        self.prompt = prompt

        if self.short_name and len(self.short_name) > 1:
            raise errors.ParamError(
                f"Parameter {self.param_name}'s shortened name is longer than 1 character",
                self,
            )

    @property
    def schema(self):
        return {
            "argument_name": self.argument_name,
            "type": self.type,
            "param_name": self.param_name,
            "short_name": self.short_name,
            "default": self.default,
        }

    @property
    def is_argument(self):
        return False

    @property
    def is_keyword(self):
        return False

    @property
    def is_option(self):
        return False

    @property
    def is_flag(self):
        return False

    @property
    def is_injected(self):
        return False

    @property
    def is_optional(self):
        return self.type.is_optional_type or self.default is not MISSING

    @property
    def is_required(self):
        return not self.is_optional

    @cached_property
    def nargs(self) -> at.NArgs:
        if (
            utils.safe_issubclass(self.type.origin, tuple)
            and self.type.sub_types
            and self.type.sub_types[-1].origin is not Ellipsis
        ):
            return len(self.type.sub_types)
        elif utils.safe_issubclass(self.type.origin, (tuple, list, set)):
            if self.default is MISSING:
                return "+"

            return "*"

        return None

    @cached_property
    def action(self) -> Action:
        return Action.STORE

    def process_parsed_result(self, res: at.ParseResult, ctx: Context):
        return res.get(self.param_name)

    def get_param_names(self) -> list[str]:
        return []


class ArgumentParam(
    Param[t.Any],
    members=["argument_name", "param_name", "default"],
):
    @property
    def is_argument(self):
        return True

    def get_param_names(self) -> list[str]:
        return [self.param_name]


class KeywordParam(Param[T]):
    def is_keyword(self):
        return True

    def get_param_names(self) -> list[str]:
        if self.short_name:
            return [f"-{self.short_name}", f"--{self.param_name}"]

        return [f"--{self.param_name}"]


class OptionParam(KeywordParam[t.Any]):
    def is_option(self):
        return True


class FlagParam(KeywordParam[bool]):
    def is_flag(self):
        return True

    @cached_property
    def action(self) -> Action:
        if self.default:
            return Action.STORE_FALSE

        return Action.STORE_TRUE


class InjectedParam(Param):
    """Injected Params are params whose values do
    not come from the command line, but from a dependancy injection.
    Used to get access to things like the arc Context and State
    """

    callback: t.Callable

    def is_injected(self):
        return True
