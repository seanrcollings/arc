"""Module for all Alias types. Alias types are types that handle to conversion for other types.
All builtin types (int, str, float, etc...) have a corresponding Alias type.
"""
from __future__ import annotations
import enum
import typing as t
import pathlib

from arc import errors, utils, logging
from arc.color import colorize, fg
from arc.types.helpers import join_or, safe_issubclass


if t.TYPE_CHECKING:
    from arc.types.helpers import TypeInfo
    from arc.typing import Annotation
    from arc.execution_state import ExecutionState

logger = logging.getArcLogger("ali")


@t.runtime_checkable
class TypeProtocol(t.Protocol):
    # name: t.ClassVar[t.Optional[str]]
    # allow_missing: t.ClassVar[t.Optional[bool]]

    @classmethod
    def __convert__(cls, value, *args):
        ...


class Alias:
    """Parent class for all aliases. Stores references to all
    known alias types and handles resolving them. Additionally,
    it provides a convenience wrapper for alias types by implementing
    a custom `cls.__convert__()` that calls `cls.convert()` for non-paramaterized
    types and `cls.g_convert()` for generic types.
    """

    aliases: dict[Annotation, type[TypeProtocol]] = {}
    alias_for: t.ClassVar[Annotation]
    name: t.ClassVar[t.Optional[str]] = None
    convert: t.Callable
    g_convert: t.Callable

    @classmethod
    def __convert__(cls, value, typ: TypeInfo, state: ExecutionState):
        if cls.name:
            typ._name = cls.name

        if not typ.sub_types:
            return utils.dispatch_args(cls.convert, value, typ, state)
        else:
            return utils.dispatch_args(cls.g_convert, value, typ, state)

    def __init_subclass__(cls, register: bool = True):
        if register:
            Alias.aliases[cls.alias_for] = cls  # type: ignore

    @classmethod
    def resolve(cls, info: TypeInfo) -> type[TypeProtocol]:
        """Handles resolving alias types"""
        annotation = info.origin
        if safe_issubclass(annotation, TypeProtocol):
            return annotation
        elif annotation in cls.aliases:
            # Type is a key
            # We perform this check once before hand
            # because some typing types don't have
            # the mro() method
            return cls.aliases[annotation]
        else:
            # Type is a subclass of a key
            for parent in annotation.mro():
                if parent in cls.aliases:
                    return cls.aliases[parent]

        name = colorize(annotation.__name__, fg.YELLOW)
        raise errors.MissingParamType(
            f"{name} is not a valid type. "
            f"Please ensure that {name} conforms to the custom type protocol "
            f"or that there is a alias type registered for it: "
            "<link stub>"
        )


# Builtin Types ---------------------------------------------------------------------------------


class String(str, Alias):
    alias_for = str

    @classmethod
    def convert(cls, value: t.Any) -> str:  # type: ignore
        return str(value)


class Bytes(bytes, Alias):
    alias_for = bytes

    @classmethod
    def convert(cls, value: t.Any) -> bytes:  # type: ignore
        return str(value).encode()


class _NumberBaseParamType(Alias, register=False):
    alias_for: t.ClassVar[type]

    @classmethod
    def convert(cls, value: t.Any, typ: TypeInfo) -> t.Any:  # type: ignore
        try:
            return cls.alias_for(value)
        except ValueError as e:
            raise errors.ConversionError(
                value, f"{value} is not a valid {typ.name}"
            ) from e


class Int(int, _NumberBaseParamType):
    alias_for = int
    name = "integer"


class Float(float, _NumberBaseParamType):
    alias_for = float
    name = "float"


TRUE_VALUES = {"true", "t", "yes", "1"}
FALSE_VALUES = {"false", "f", "no", "0"}


class Bool(int, Alias):
    alias_for = bool
    name = "boolean"

    @classmethod
    def convert(cls, value: t.Any) -> bool:  # type: ignore
        if isinstance(value, str):
            if value.isnumeric():
                return bool(int(value))

            value = value.lower()
            if value in TRUE_VALUES:
                return True
            elif value in FALSE_VALUES:
                return False

        return bool(value)


class _CollectionAlias(Alias, register=False):
    alias_for: t.ClassVar[type]

    @classmethod
    def convert(cls, value: str):  # type: ignore
        return cls.alias_for(value.split(","))

    @classmethod
    def g_convert(cls, value: str, typ: TypeInfo, state):  # type: ignore
        lst = cls.convert(value)
        sub = typ.sub_types[0]
        sub_type = Alias.resolve(sub)

        try:
            return cls.alias_for([sub_type.__convert__(v, sub, state) for v in lst])
        except errors.ConversionError as e:
            raise errors.ConversionError(
                value,
                f"{value} is not a valid {typ.name} of {sub.name}s",
            ) from e


class List(list, _CollectionAlias):
    alias_for = list


class Set(set, _CollectionAlias):
    alias_for = set


class Tuple(tuple, _CollectionAlias):
    alias_for = tuple

    @classmethod
    def g_convert(cls, value: str, info: TypeInfo, state: ExecutionState):  # type: ignore
        tup = cls.convert(value)

        # Arbitraryily sized tuples
        if info.sub_types[-1].origin is Ellipsis:
            return super().g_convert(value, info, state)

        # Statically sized tuples
        if len(info.sub_types) != len(tup):
            raise errors.ConversionError(
                value, f"only {len(info.sub_types)} elements are allowed"
            )

        return tuple(
            utils.dispatch_args(
                Alias.resolve(item_type).__convert__, item, item_type, state
            )
            for item_type, item in zip(info.sub_types, tup)
        )


# Typing types ---------------------------------------------------------------------------------


class UnionAlias(Alias):
    alias_for = t.Union

    @classmethod
    def g_convert(cls, value: t.Any, info: TypeInfo, state):  # type: ignore

        for sub in info.sub_types:
            try:
                type_cls = Alias.resolve(sub)
                return utils.dispatch_args(type_cls.__convert__, value, sub, state)
            except Exception:
                ...

        raise errors.ConversionError(
            value,
            f"must be a {join_or(list(sub.name for sub in info.sub_types))}",
        )


class LiteralAlias(Alias):
    alias_for = t.Literal

    @classmethod
    def g_convert(cls, value: t.Any, info: TypeInfo):  # type: ignore
        for sub in info.sub_types:
            if str(sub.base) == value:
                return sub.base

        raise errors.ConversionError(
            value, f"must be {join_or(list(sub.base for sub in info.sub_types))}"
        )


# Stdlib types ---------------------------------------------------------------------------------


class Enum(Alias):
    alias_for = enum.Enum

    @classmethod
    def convert(cls, value: t.Any, info: TypeInfo[enum.Enum]):  # type: ignore
        try:
            if issubclass(info.origin, enum.IntEnum):
                return info.origin(int(value))

            return info.origin(value)
        except ValueError as e:
            raise errors.ConversionError(
                value,
                f"must be {join_or([m.value for m in info.origin.__members__.values()])}",
            ) from e


class Path(Alias):
    alias_for = pathlib.Path

    @classmethod
    def convert(cls, value: t.Any):  # type: ignore
        return pathlib.Path(value)


class IO(Alias):
    alias_for = t.IO

    @classmethod
    def convert(cls, value: str, info: TypeInfo) -> t.IO:
        try:
            file = open(value, **cls.open_args(info))
            return file
        except FileNotFoundError as e:
            raise errors.ConversionError(value, f"No file named {value}") from e

    @classmethod
    def open_args(cls, info):
        arg = info.annotations[0]
        if isinstance(arg, str):
            return {"mode": arg}
        if isinstance(arg, dict):
            return arg

    @classmethod
    def __cleanup__(cls, handle: t.IO):
        logger.debug("Closing File handle for: %s", handle.name)
        handle.close()
