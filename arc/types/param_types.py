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
from arc.types.helpers import join_or, isclassmethod, safe_issubclass
from arc.types.var_types import VarPositional, VarKeyword
from arc.utils import symbol

if t.TYPE_CHECKING:
    from arc.command.param import Param

logger = logging.getArcLogger("prt")


MISSING = symbol("MISSING")

Annotation = t.Union[t._SpecialForm, type]

# pylint: disable=abstract-method,inconsistent-return-statements


class ParamType:
    param: Param
    state: ExecutionState

    cleanup: t.Optional[types.MethodType] = None

    _param_type_map: dict[Annotation, type[ParamType]] = {}
    _param_type_cache: dict[Annotation, ParamType] = {}

    # Optional values that can be defined in subclasses
    class Config:
        name: str = "param"
        handles: t.ClassVar[t.Optional[Annotation]] = None
        allow_missing: t.ClassVar[bool] = False
        allowed_annotated_args: t.ClassVar[int] = 0

    def __init__(self, annotation: Annotation = None, annotated_args: tuple = None):
        annotation = annotation or self.Config.handles
        annotated_args = annotated_args or ()

        if len(annotated_args) > self.Config.allowed_annotated_args:
            raise errors.ArcError(
                f"{self.Config.name} permits {self.Config.allowed_annotated_args} "
                f"annotated arguments. Recieved {len(annotated_args)}"
            )

        self.annotation = annotation
        self.origin = t.get_origin(annotation)
        self.type_args = t.get_args(annotation)
        self.annotated_args = annotated_args

    def __repr__(self):
        return f"{self.__class__.__name__}(annotation={self.annotation})"

    def __call__(self, value: t.Any, param: Param, state: ExecutionState):
        if value is MISSING and not self.Config.allow_missing:
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

                raise errors.InvalidParamaterError(
                    f"accepts: {self.Config.name}, was: {value}",
                    self.param,
                    self.state,
                ) from e

        return value

    def __init_subclass__(cls, cache: bool = False) -> None:
        if getattr(cls, "Config", None):
            ParamType.update_config(cls)
        else:
            cls.Config = ParamType.Config  # type: ignore

        if cls.Config.handles:
            cls._param_type_map[cls.Config.handles] = cls

            if cache:
                cls._param_type_cache[cls.Config.handles] = cls()

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

        if safe_issubclass(base_type, CustomType):
            param_type = CustomParamType
        elif base_type in cls._param_type_cache:
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
            raise errors.MissingParamType(f"No Param type for {base_type}")

        return param_type(kind, annotated_args)

    @classmethod
    def update_config(cls, param_type):
        """Updates param_type.Config with any missing values that are present
        on cls.Config. A form of "dirty inhertiance" so the configuration classes
        don't need to perform any inhertiance and we still get valid values
        """
        parent_props = [prop for prop in dir(cls.Config) if not prop.startswith("__")]
        for prop in parent_props:
            child_prop = getattr(param_type.Config, prop, None)
            if child_prop is None:
                setattr(param_type.Config, prop, getattr(cls.Config, prop))


@t.runtime_checkable
class CustomType(t.Protocol):
    @classmethod
    def __convert__(cls, value, param_type: CustomParamType) -> CustomType:
        ...


class CustomParamType(ParamType):
    annotation: type[CustomType]

    def __init__(self, annotation: type[CustomType], annotated_args: t.Any = None):
        if not isclassmethod(getattr(annotation, "__convert__", None)):
            raise errors.ArgumentError(
                "Custom types must have a classmethod __convert__"
            )

        type_config: type = getattr(annotation, "Config", None)
        if type_config:
            self.Config = type_config  # type: ignore
            ParamType.update_config(self)

        super().__init__(annotation, annotated_args)

    def convert(self, value: str):
        return self.annotation.__convert__(value, self)

    def g_convert(self, value: str):
        return self.annotation.__convert__(value, self)


## Basic Types


class StringParamType(ParamType, cache=True):
    class Config:
        name = "string"
        handles = str

    def convert(self, value: t.Any) -> str:
        return str(value)


class _NumberBaseParamType(ParamType, cache=True):
    class Config:
        name: str
        handles: t.ClassVar[type]

    def convert(self, value: t.Any) -> t.Any:
        try:
            return self.Config.handles(value)
        except ValueError:
            return self.fail(f"{value} is not a valid {self.Config.name}")


class IntParamType(_NumberBaseParamType, cache=True):
    class Config:
        name = "integer"
        handles = int


class FloatParamType(_NumberBaseParamType, cache=True):
    class Config:
        name = "float"
        handles = float


class BytesParamType(ParamType, cache=True):
    class Config:
        name = "bytes"
        handles = bytes

    def convert(self, value: t.Any) -> bytes:
        return str(value).encode()


class BoolParamType(ParamType, cache=True):
    class Config:
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


class _CollectionParamType(ParamType):
    class Config:
        name: str
        handles: t.ClassVar[type]

    def convert(self, value: str):
        return self.Config.handles(value.split(","))

    def g_convert(self, value: str):
        lst = self.convert(value)
        param_type = ParamType.get_param_type(self.type_args[0])
        try:
            return self.Config.handles(
                [param_type(v, self.param, self.state) for v in lst]
            )
        except errors.InvalidParamaterError:
            return self.fail(
                f"{value} is not a valid {self.Config.name} of {param_type.Config.name}s"
            )


class ListParamType(_CollectionParamType):
    class Config:
        name = "list"
        handles = list


class SetParamType(_CollectionParamType):
    class Config:
        name = "set"
        handles = set


class TupleParamType(_CollectionParamType):
    class Config:
        name = "tuple"
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
    class Config:
        name = "Union"
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

        self.fail(
            f"{value} must be a {join_or(list(p.Config.name for p in param_types))}"
        )


class LiteralParamType(ParamType):
    class Config:
        name = "Literals"
        handles = t.Literal

    def g_convert(self, value: t.Any):
        if value in self.type_args:
            return value

        raise self.fail(f"{value} must be {join_or(self.type_args)}")


### Std Lib Types


class EnumParamType(ParamType):
    annotation: type[enum.Enum]

    class Config:
        name = "Eumeration"
        handles = enum.Enum

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
    class Config:
        name = "FilePath"
        handles = Path

    def convert(self, value: t.Any) -> Path:
        return Path(value)


class FileParamType(ParamType):
    _file_handle: t.IO

    class Config:
        name = "filepath"
        handles = t.IO
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


class VarPositionalParamType(ParamType):
    class Config:
        name = "*args"
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
    class Config:
        name = "**kwargs"
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
