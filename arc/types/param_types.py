"""Module containing internal types
that represent a specific CLI Paramater's type.
Used to transform user input into the correct type value
"""
from __future__ import annotations
import enum
import typing as t
import types
from pathlib import Path
from arc import logging
from arc import errors
from arc.types.context import Context
from arc.config import config
from arc.color import colorize, fg
from arc.execution_state import ExecutionState
from arc.types.helpers import join_or, isclassmethod
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
    param: Param
    state: ExecutionState

    # Optional values that can be defined in subclasses
    name: str = "param"
    cleanup: t.Optional[types.MethodType] = None
    handles: t.ClassVar[t.Optional[Annotation]] = None
    allow_missing: t.ClassVar[bool] = False
    allowed_annotated_args: t.ClassVar[int] = 0

    _param_type_map: dict[Annotation, type[ParamType]] = {}
    _param_type_cache: dict[Annotation, ParamType] = {}

    def __init__(self, annotation: Annotation = None, annotated_args: tuple = None):
        annotation = annotation or self.handles
        annotated_args = annotated_args or ()

        if len(annotated_args) > self.allowed_annotated_args:
            raise errors.ArcError(
                f"{self.name} permits {self.allowed_annotated_args} "
                f"annotated arguments. Recieved {len(annotated_args)}"
            )

        self.annotation = annotation
        self.origin = t.get_origin(annotation)
        self.type_args = t.get_args(annotation)
        self.annotated_args = annotated_args

    def __repr__(self):
        return f"{self.__class__.__name__}(annotation={self.annotation})"

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
                        f"accepts: {self.name}, was: {value}", self.param, self.state
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
        annotated_args: t.Optional[tuple] = None

        if base_type is t.Annotated:
            args = t.get_args(kind)
            base_type = args[0]
            kind = base_type
            annotated_args = args[1:]

        param_type: t.Optional[type[ParamType]] = None

        try:
            if issubclass(base_type, CustomType):
                param_type = CustomParamType
        except TypeError:
            ...

        if base_type in cls._param_type_cache:
            # Type is cached
            return cls._param_type_cache[base_type]
        elif base_type in cls._param_type_map:
            # Type is a key
            # We perform this check once before hand
            # because some typing types don't have
            # the mro() method
            param_type = cls._param_type_map[base_type]
        else:
            # Type is a subclass of a key
            for parent in base_type.mro():
                if parent in cls._param_type_map:
                    param_type = cls._param_type_map[parent]

        if not param_type:
            raise errors.ArcError(f"No Param type for {base_type}")

        return param_type(kind, annotated_args)


@t.runtime_checkable
class CustomType(t.Protocol):
    @classmethod
    def __convert__(cls, value, param_type: CustomParamType) -> CustomType:
        ...


class CustomParamType(ParamType):
    annotation: type[CustomType]

    def __init__(self, annotation: type[CustomType], annotated_args: t.Any = None):
        if not isclassmethod(getattr(annotation, "__convert__")):
            raise errors.ArgumentError(
                "Custom types must have a classmethod __convert__"
            )

        type_config: dict = getattr(annotation, "__config__", None)
        if type_config:
            for key, value in type_config.items():
                setattr(self, key, value)

        super().__init__(annotation, annotated_args)

    def convert(self, value: str):
        return self.annotation.__convert__(value, self)

    def g_convert(self, value: str):
        return self.annotation.__convert__(value, self)


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
            return self.fail(f"{value} is not a valid {self.name}")


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
        param_type = ParamType.get_param_type(self.type_args[0])
        try:
            return self.handles([param_type(v, self.param, self.state) for v in lst])
        except errors.InvalidParamaterError:
            return self.fail(
                f"{value} is not a valid {self.name} of {param_type.name}s"
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
        if self.type_args[-1] is Ellipsis:
            return super().g_convert(value)

        # Statically sized tuples
        if len(self.type_args) != len(tup):
            return self.fail(f"only allow {len(self.type_args)} elements")

        return tuple(
            ParamType.get_param_type(item_type).convert(item)
            for item_type, item in zip(self.type_args, tup)
        )


# Typing Types
class UnionParamType(ParamType):
    accepts = "Union"
    handles = t.Union

    def g_convert(self, value: t.Any):
        param_types: set[ParamType] = set()

        for arg in self.type_args:
            try:
                param_type = ParamType.get_param_type(arg)
                param_types.add(param_type)
                return param_type(value, self.param, self.state)
            except errors.ArcError:
                ...

        self.fail(f"{value} must be a {join_or(list(p.name for p in param_types))}")


class LiteralParamType(ParamType):
    accepts = "Literals"
    handles = t.Literal

    def g_convert(self, value: t.Any):
        if value in self.type_args:
            return value

        raise self.fail(f"{value} must be {join_or(self.type_args)}")


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
        param_type = ParamType.get_param_type(self.type_args[0])
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
        param_type = ParamType.get_param_type(self.type_args[0])
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
        arg = self.annotated_args[0]
        if isinstance(arg, str):
            return {"mode": arg}
        if isinstance(arg, dict):
            return arg


class RangeParamType(ParamType):
    accepts = "range"
    handles = Range
    allowed_annotated_args = 2
    annotated_args: tuple[int, int]

    class NoRangeBounds(errors.ArgumentError):
        ...

    def convert(self, value: str) -> Range:
        if not self.annotated_args:
            raise RangeParamType.NoRangeBounds(
                "Ranges must have an associated lower / upper bound.\n"
                "Replace `Range` in your function definition with"
                "`typing.Annotated[Range, <lower>, <upper>]`"
            )

        num: int = ParamType.get_param_type(int)(value, self.param, self.state)
        try:
            return Range(num, *self.annotated_args)
        except AssertionError:
            return self.fail(f"must be a number between {self.annotated_args}")
