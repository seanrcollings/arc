"""Module containing internal types
that represent a specific CLI Paramater's type.
Used to transform user input into the correct type value
"""
from __future__ import annotations
import enum
import typing as t
import types
import logging
from pathlib import Path
from arc import errors
from arc.types.context import Context
from arc.config import config
from arc.color import colorize, fg
from arc.execution_state import ExecutionState
from arc.utils import symbol

if t.TYPE_CHECKING:
    from arc.command.param import Param

logger = logging.getLogger("arc_logger")


MISSING = symbol("MISSING")

Annotation = t.Union[t._SpecialForm, type]

# pylint: disable=abstract-method

# TODO:
# - Add human-readable error-handling for types
# - Get VarPositonal and VarKeyword Working
# - Make a more user-friendly api for creating custom types


class ParamType:
    name: t.ClassVar[str]
    param: Param
    state: ExecutionState
    cleanup: t.Optional[types.MethodType] = None
    handles: t.ClassVar[t.Optional[Annotation]] = None
    allow_missing: bool = False

    _param_type_map: dict[Annotation, type[ParamType]] = {}
    _param_type_cache: dict[Annotation, ParamType] = {}

    def __init__(self, annotation: Annotation = None):
        annotation = annotation or self.handles
        self.annotation = annotation
        self.origin = t.get_origin(annotation)
        self.args = t.get_args(annotation)

    def __repr__(self):
        return f"{self.name}(annotation={self.annotation})"

    def __call__(self, value: t.Any, param: Param, state: ExecutionState):
        if value is MISSING and not self.allow_missing:
            if param.is_positional:
                message = (
                    "No value provided for required positional argument: "
                    + colorize(param.arg_alias, fg.YELLOW)
                )

            else:
                message = "No value provided for required option " + colorize(
                    config.flag_denoter + param.arg_alias, fg.YELLOW
                )

            raise errors.ArgumentError(message)

        if self.cleanup:
            self.param._cleanup_funcs.add(self.cleanup)

        if value is not None:
            self.param = param
            self.state = state
            try:
                if self.is_generic:
                    value = self.g_convert(value)
                else:
                    value = self.convert(value)
            except Exception as e:
                raise errors.ArgumentError(self.fail(value, e)) from e

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

    def fail(self, value: t.Any, e: Exception):
        if isinstance(e, errors.ConversionError):
            value = e.value
            expected = e.expected
            helper = e.helper_text
        else:
            expected = self.name
            helper = ""

        if expected.startswith(("a", "e", "i", "o", "u")):
            expected = "an " + expected
        else:
            expected = "a " + expected

        return (
            f"Paramater {colorize(self.param.arg_alias, fg.BLUE)} expected "
            f"{expected}, but was "
            f"{colorize(value, fg.YELLOW)}. {helper}"
        )

    @classmethod
    def get_param_type(cls, kind: type, default=None):
        # Unwrap to handle generic types (list[int])
        origin = t.get_origin(kind) or kind

        try:
            if issubclass(origin, ParamType):
                return kind()
        except TypeError:
            ...

        if origin in cls._param_type_cache:
            return cls._param_type_cache[origin]

        # Type is a key
        # We perform this check once before hand
        # because some typing types don't have
        # the mro() method
        if origin in cls._param_type_map:
            return cls._param_type_map[origin](kind)

        # Type is a subclass of a key
        for parent in origin.mro():
            if parent in cls._param_type_map:
                return cls._param_type_map[parent](kind)

        raise errors.ArcError(f"No Param type for {kind}")


## Basic Types


class StringParamType(ParamType, cache=True):
    name = "string"
    handles = str

    def convert(self, value: t.Any) -> str:
        return str(value)


class IntParamType(ParamType, cache=True):
    name = "integer"
    handles = int

    def convert(self, value: t.Any) -> int:
        return int(value)


class FloatParamType(ParamType, cache=True):
    name = "integer"
    handles = float

    def convert(self, value: t.Any) -> float:
        return float(value)


class BytesParamType(ParamType, cache=True):
    name = "bytes"
    handles = bytes

    def convert(self, value: t.Any) -> bytes:
        return str(value).encode()


class BoolParamType(ParamType, cache=True):
    name = "boolean"
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
        return self.handles(
            [
                ParamType.get_param_type(self.args[0])(v, self.param, self.state)
                for v in lst
            ]
        )


class ListParamType(CollectionParamType):
    name = "list"
    handles = list


class SetParamType(CollectionParamType):
    name = "set"
    handles = set


class TupleParamType(CollectionParamType):
    name = "tuple"
    handles = tuple

    def g_convert(self, value: str) -> tuple:
        tup = self.convert(value)

        # Arbitraryily sized tuples
        if self.args[-1] is Ellipsis:
            param_type = ParamType.get_param_type(self.args[0])
            return tuple(param_type.convert(item) for item in tup)

        if len(self.args) != len(tup):
            raise TypeError("Incorrect number of elements")

        # statically sized tuples
        return tuple(
            ParamType.get_param_type(item_type).convert(item)
            for item_type, item in zip(self.args, tup)
        )


# Typing Types
class UnionParamType(ParamType):
    name = "Union"
    handles = t.Union

    def g_convert(self, value: t.Any):

        for arg in self.args:
            try:
                return ParamType.get_param_type(arg)(value, self.param, self.state)
            except:
                ...

        raise TypeError()


class LiteralParamType(ParamType):
    name = "Literals"
    handles = t.Union

    def g_convert(self, value: t.Any):
        if value in self.args:
            return value

        raise TypeError("Not a valid option")


### Std Lib Types


class EnumParamType(ParamType):
    name = "Eumeration"
    handles = enum.Enum
    annotation: type[enum.Enum]

    def convert(self, value: t.Any):
        return self.annotation(value)


class PathParamType(ParamType, cache=True):
    name = "FilePath"
    handles = Path

    def convert(self, value: t.Any) -> Path:
        return Path(value)


### Custom Types

# TODO: figure out how these were supposed to work, I dont' remember :(

T = t.TypeVar("T")


class VarPositional(list[T], ParamType):
    def convert(self, _value: t.Any) -> list:
        values = self.state.parsed["pos_values"]
        self.state.parsed["pos_values"] = []
        return values

    def g_convert(self, _value: t.Any) -> list[T]:
        lst = self.convert(None)
        param_type = ParamType.get_param_type(self.args[0])
        return [param_type.convert(v) for v in lst]


class VarKeyword(dict[str, T], ParamType):
    def convert(self, _value: t.Any) -> dict[str, str]:
        return {}

    def g_convert(self, value: t.Any) -> dict[str, T]:
        return {}


class ContextParamType(ParamType):
    name = "Context"
    annotation: type
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


class File:
    class FileType(t.IO, ParamType, cache=True):
        name = "File"
        _file_handles: list[t.IO]
        mode: str

        def convert(self, value: str) -> t.IO:
            file = open(value, self.mode)
            self._file_handles.append(file)
            return file

        @classmethod
        def cleanup(cls):
            for handle in cls._file_handles:
                logger.debug("Closing File handle for: %s", handle.name)
                handle.close()

        def __init_subclass__(cls, **kwargs):
            cls._file_handles = []
            cls.name = f"File.{cls.__name__}"

            super().__init_subclass__(cls, **kwargs)

    class Read(FileType):
        mode = "r"

    class Write(FileType):
        mode = "w"

    class ReadWrite(FileType):
        mode = "rw"

    class ReadCreate(FileType):
        mode = "r+"

    class WriteCreate(FileType):
        mode = "r+"

    class Append(FileType):
        mode = "a"
