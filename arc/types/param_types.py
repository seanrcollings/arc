"""Module containing internal types
that represent a specific CLI Paramater's type.
Used to transform user input into the correct type value
"""
from __future__ import annotations
import enum
import typing as t
import types
from arc import logging
from pathlib import Path
from arc import errors
from arc.types.context import Context
from arc.config import config
from arc.color import colorize, fg
from arc.execution_state import ExecutionState
from arc.types.helpers import join_or
from arc.types.range import Range
from arc.types.var_types import VarPositional, VarKeyword
from arc.utils import symbol

if t.TYPE_CHECKING:
    from arc.command.param import Param

logger = logging.getArcLogger("prt")


MISSING = symbol("MISSING")

Annotation = t.Union[t._SpecialForm, type]

# pylint: disable=abstract-method,inconsistent-return-statements

# TODO:
# - Make a more user-friendly api for creating custom types


class ParamType:
    accepts: t.ClassVar[str]
    param: Param
    state: ExecutionState
    cleanup: t.Optional[types.MethodType] = None
    handles: t.ClassVar[t.Optional[Annotation]] = None
    allow_missing: bool = False
    allowed_annotated_args: t.ClassVar[int] = 0

    _param_type_map: dict[Annotation, type[ParamType]] = {}
    _param_type_cache: dict[Annotation, ParamType] = {}

    def __init__(self, annotation: Annotation = None, type_info: t.Any = None):
        annotation = annotation or self.handles
        self.annotation = annotation
        self.type_info = type_info
        self.origin = t.get_origin(annotation)
        self.args = t.get_args(annotation)

    def __repr__(self):
        return f"{self.__class__.__name__}(oannotation={self.annotation})"

    def __call__(self, value: t.Any, param: Param, state: ExecutionState):
        if value is MISSING and not self.allow_missing:
            if param.is_positional:
                message = (
                    "No value provided for required positional argument: "
                    + colorize(param.arg_alias, fg.YELLOW)
                )

            else:
                message = "No value provided for required option " + colorize(
                    config.flag_prefix + param.arg_alias, fg.YELLOW
                )

            raise errors.MissingArgError(message)

        if value is not None:
            self.param = param
            self.state = state

            if self.cleanup:
                self.param._cleanup_funcs.add(self.cleanup)

            try:
                if self.is_generic:
                    value = self.g_convert(value)
                else:
                    value = self.convert(value)
            except Exception as e:
                if self.cleanup:
                    self.param._cleanup_funcs.remove(self.cleanup)

                if isinstance(e, errors.InvalidParamaterError):
                    raise
                else:
                    raise errors.InvalidParamaterError(
                        f"accepts: {self.accepts}, was: {value}", self.param, self.state
                    ) from e

        return value

    def __init_subclass__(cls, cache: bool = False) -> None:
        if cls.handles:
            cls._param_type_map[cls.handles] = cls

            if cache:
                cls._param_type_cache[cls.handles] = cls()

        return super().__init_subclass__()

    @property
    def is_generic(self):
        return self.origin is not None

    def convert(self, value: t.Any) -> t.Any:
        raise NotImplementedError(f"{self!r} does not support non Generic types")

    def g_convert(self, value: t.Any) -> t.Any:
        """Type supports generics (list[int])"""
        raise NotImplementedError(f"{self!r} does not support Generic types")

    def fail(self, message: str):
        raise errors.InvalidParamaterError(message, self.param, self.state)

    @classmethod
    def get_param_type(cls, kind: type):
        # Unwrap to handle generic types (list[int])
        base_type = t.get_origin(kind) or kind
        type_info: t.Optional[tuple] = None

        if base_type is t.Annotated:
            args = t.get_args(kind)
            base_type = args[0]
            kind = base_type
            type_info = args[1:]

        param_type = None

        if base_type in cls._param_type_cache:
            return cls._param_type_cache[base_type]

        # Type is a key
        # We perform this check once before hand
        # because some typing types don't have
        # the mro() method
        elif base_type in cls._param_type_map:
            param_type = cls._param_type_map[base_type]

        else:
            # Type is a subclass of a key
            for parent in base_type.mro():
                if parent in cls._param_type_map:
                    param_type = cls._param_type_map[parent]

        if not param_type:
            raise errors.ArcError(f"No Param type for {base_type}")

        if type_info:
            if len(type_info) > param_type.allowed_annotated_args:
                raise errors.ArcError(
                    f"{param_type.accepts} permits {param_type.allowed_annotated_args} "
                    f"annotated arguments. Recieved {len(type_info)}"
                )

            if param_type.allowed_annotated_args == 1:
                type_info = type_info[0]

        return param_type(kind, type_info)


## Basic Types


class StringParamType(ParamType, cache=True):
    accepts = "string"
    handles = str

    def convert(self, value: t.Any) -> str:
        return str(value)


class _NumberBaseParamType(ParamType, cache=True):
    handles: t.ClassVar[type]

    def convert(self, value: t.Any) -> t.Any:
        try:
            return self.handles(value)
        except ValueError:
            return self.fail(f"{value} is not a valid {self.accepts}")


class IntParamType(_NumberBaseParamType, cache=True):
    accepts = "integer"
    handles = int


class FloatParamType(_NumberBaseParamType, cache=True):
    accepts = "float"
    handles = float


class BytesParamType(ParamType, cache=True):
    accepts = "bytes"
    handles = bytes

    def convert(self, value: t.Any) -> bytes:
        return str(value).encode()


class BoolParamType(ParamType, cache=True):
    accepts = "boolean"
    handles = bool

    def convert(self, value: t.Any) -> bool:
        if isinstance(value, str):
            if value.isnumeric():
                return bool(int(value))

            value = value.lower()
            if value in ("true", "t"):
                return True
            elif value in ("false", "f"):
                return False

        return bool(value)


class CollectionParamType(ParamType):
    handles: t.ClassVar[type]

    def convert(self, value: str):
        return self.handles(value.split(","))

    def g_convert(self, value: str):
        lst = self.convert(value)
        param_type = ParamType.get_param_type(self.args[0])
        try:
            return self.handles([param_type(v, self.param, self.state) for v in lst])
        except errors.InvalidParamaterError:
            return self.fail(
                f"{value} is not a valid {self.accepts} of {param_type.accepts}s"
            )


class ListParamType(CollectionParamType):
    accepts = "list"
    handles = list


class SetParamType(CollectionParamType):
    accepts = "set"
    handles = set


class TupleParamType(CollectionParamType):
    accepts = "tuple"
    handles = tuple

    def g_convert(self, value: str) -> tuple:
        tup = self.convert(value)

        # Arbitraryily sized tuples
        if self.args[-1] is Ellipsis:
            return super().g_convert(value)

        # Statically sized tuples
        if len(self.args) != len(tup):
            return self.fail(f"only allow {len(self.args)} elements")

        return tuple(
            ParamType.get_param_type(item_type).convert(item)
            for item_type, item in zip(self.args, tup)
        )


# Typing Types
class UnionParamType(ParamType):
    accepts = "Union"
    handles = t.Union

    def g_convert(self, value: t.Any):
        param_types: set[ParamType] = set()

        for arg in self.args:
            try:
                param_type = ParamType.get_param_type(arg)
                param_types.add(param_type)
                return param_type(value, self.param, self.state)
            except errors.ArcError:
                ...

        self.fail(f"{value} must be a {join_or(list(p.accepts for p in param_types))}")


class LiteralParamType(ParamType):
    accepts = "Literals"
    handles = t.Literal

    def g_convert(self, value: t.Any):
        if value in self.args:
            return value

        raise self.fail(f"{value} must be {join_or(self.args)}")


### Std Lib Types


class EnumParamType(ParamType):
    accepts = "Eumeration"
    handles = enum.Enum
    annotation: type[enum.Enum]

    def convert(self, value: t.Any):
        try:
            if issubclass(self.annotation, enum.IntEnum):
                return self.annotation(int(value))

            return self.annotation(value)
        except ValueError:
            self.fail(
                f"must be {join_or([m.value for m in self.annotation.__members__.values()])}"
            )


class PathParamType(ParamType, cache=True):
    accepts = "FilePath"
    handles = Path

    def convert(self, value: t.Any) -> Path:
        return Path(value)


### Custom Types


class VarPositionalParamType(ParamType):
    accepts = "*args"
    handles = VarPositional
    allow_missing = True

    def convert(self, _value: t.Any) -> list:
        values = self.state.parsed["pos_values"]
        self.state.parsed["pos_values"] = []
        return values

    def g_convert(self, _value: t.Any) -> list[t.Any]:
        lst = self.convert(None)
        param_type = ParamType.get_param_type(self.args[0])
        return [param_type(v, self.param, self.state) for v in lst]


class VarKeywordParamType(ParamType):
    accepts = "**kwargs"
    handles = VarKeyword
    allow_missing = True

    def convert(self, _value: t.Any) -> dict[str, t.Any]:
        assert self.state.executable
        kwargs = {
            name: value
            for name, value in self.state.parsed["key_values"].items()
            if name
            not in self.state.executable.key_params | self.state.executable.flag_params
        }
        self.state.parsed["key_values"] = {
            name: value
            for name, value in self.state.parsed["key_values"].items()
            if name not in kwargs
        }
        return kwargs

    def g_convert(self, value: t.Any) -> dict[str, t.Any]:
        values = self.convert(None)
        param_type = ParamType.get_param_type(self.args[0])
        return {
            name: param_type(value, self.param, self.state)
            for name, value in values.items()
        }


class ContextParamType(ParamType):
    annotation: type
    accepts = "Context"
    handles = Context
    allow_missing = True

    def convert(self, value: t.Any):
        ctx: dict[str, t.Any] = {}

        if value is MISSING:
            value = {}

        ctx |= value

        for command in self.state.command_chain:
            ctx = command.context | ctx

        ctx["state"] = self.state

        return self.annotation(ctx)


class FileParamType(ParamType):
    accepts = "filepath"
    handles = t.IO
    _file_handle: t.IO
    allowed_annotated_args = 1

    def convert(self, value: str) -> t.IO:
        try:
            file = open(value, **self.open_args())
            self._file_handle = file
            return file
        except FileNotFoundError:
            return self.fail(f"No file named {value}")

    def cleanup(self):
        logger.debug("Closing File handle for: %s", self._file_handle.name)
        self._file_handle.close()

    def open_args(self):
        if isinstance(self.type_info, str):
            return {"mode": self.type_info}
        if isinstance(self.type_info, dict):
            return self.type_info


class RangeParamType(ParamType):
    accepts = "range"
    handles = Range
    allowed_annotated_args = 2
    type_info: tuple[int, int]

    class NoRangeBounds(errors.ArgumentError):
        ...

    def convert(self, value: str) -> Range:
        if not self.type_info:
            raise RangeParamType.NoRangeBounds(
                "Ranges must have an associated lower / upper bound.\n"
                "Replace `Range` in your function definition with"
                "`typing.Annotated[Range, <lower>, <upper>]`"
            )

        num: int = ParamType.get_param_type(int)(value, self.param, self.state)
        try:
            return Range(num, *self.type_info)
        except AssertionError:
            return self.fail(f"must be a number between {self.type_info}")
