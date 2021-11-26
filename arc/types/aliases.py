"""Module for all Alias types. Alias types are types that handle to conversion for other types.
All builtin types (int, str, float, etc...) have a corresponding Alias type.
"""
from __future__ import annotations

import enum
import pathlib
import typing as t
import ipaddress
import dataclasses
import _io  # type: ignore

from arc import errors, logging, utils
from arc.color import colorize, fg
from arc.types.helpers import TypeInfo, join_or, safe_issubclass

from arc.typing import Annotation

if t.TYPE_CHECKING:
    from arc.execution_state import ExecutionState


logger = logging.getArcLogger("ali")


@t.runtime_checkable
class TypeProtocol(t.Protocol):
    # name: t.ClassVar[t.Optional[str]]
    # allow_missing: t.ClassVar[t.Optional[bool]]

    @classmethod
    def __convert__(cls, value, *args):
        ...


AliasFor = t.Union[Annotation, t.Tuple[Annotation, ...]]


class Alias:
    """Parent class for all aliases. Stores references to all
    known alias types and handles resolving them. Additionally,
    it provides a convenience wrapper for alias types by implementing
    a custom `cls.__convert__()` that calls `cls.convert()` for non-paramaterized
    types and `cls.g_convert()` for generic types.
    """

    aliases: dict[Annotation, type[TypeProtocol]] = {}
    alias_for: t.ClassVar[AliasFor] = None  # type: ignore
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

    def __init_subclass__(cls, of: t.Optional[AliasFor] = None):
        if of:
            cls.alias_for = of

        if cls.alias_for:
            if isinstance(cls.alias_for, tuple):
                aliases = cls.alias_for
            else:
                aliases = (cls.alias_for,)

            for alias in aliases:
                Alias.aliases[alias] = cls  # type: ignore

    @classmethod
    def resolve(cls, annotation: t.Union[TypeInfo, type]) -> type[TypeProtocol]:
        """Handles resolving alias types"""
        if isinstance(annotation, TypeInfo):
            annotation = annotation.origin

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


class StringAlias(Alias, of=str):
    @classmethod
    def convert(cls, value: t.Any) -> str:
        return str(value)


class BytesAlias(Alias, of=bytes):
    @classmethod
    def convert(cls, value: t.Any) -> bytes:
        return str(value).encode()


class _NumberBaseAlias(Alias):
    alias_for: t.ClassVar[type]

    @classmethod
    def convert(cls, value: t.Any, typ: TypeInfo) -> t.Any:
        try:
            return cls.alias_for(value)
        except ValueError as e:
            raise errors.ConversionError(
                value, f"{value} is not a valid {typ.name}"
            ) from e


class IntAlias(_NumberBaseAlias, of=int):
    name = "integer"


class FloatAlias(float, _NumberBaseAlias, of=float):
    name = "float"


TRUE_VALUES = {"true", "t", "yes", "1"}
FALSE_VALUES = {"false", "f", "no", "0"}


class BoolAlias(Alias, of=bool):
    name = "boolean"

    @classmethod
    def convert(cls, value: t.Any) -> bool:
        if isinstance(value, str):
            if value.isnumeric():
                return bool(int(value))

            value = value.lower()
            if value in TRUE_VALUES:
                return True
            elif value in FALSE_VALUES:
                return False

        return bool(value)


class _CollectionAlias(Alias):
    alias_for: t.ClassVar[type]

    @classmethod
    def convert(cls, value: str):
        return cls.alias_for(value.split(","))

    @classmethod
    def g_convert(cls, value: str, typ: TypeInfo, state):
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


class ListAlias(_CollectionAlias, of=list):
    ...


class SetAlias(_CollectionAlias, of=set):
    ...


class TupleAlias(_CollectionAlias, of=tuple):
    @classmethod
    def g_convert(cls, value: str, info: TypeInfo, state: ExecutionState):
        tup = cls.convert(value)

        # Arbitraryily sized tuples
        if cls.any_size(info):
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

    @classmethod
    def any_size(cls, info: TypeInfo):
        return info.sub_types[-1].origin is Ellipsis


class DictAlias(Alias, of=dict):
    alias_for: t.ClassVar[type]
    name = "dictionary"

    @classmethod
    def convert(cls, value: str):
        return cls.alias_for(i.split("=") for i in value.split(","))

    @classmethod
    def g_convert(cls, value, typ: TypeInfo, state):
        dct: dict = cls.convert(value)

        key_sub = typ.sub_types[0]
        key_type = Alias.resolve(key_sub)
        value_sub = typ.sub_types[1]
        value_type = Alias.resolve(value_sub)

        try:
            return cls.alias_for(
                [
                    (
                        key_type.__convert__(k, key_sub, state),
                        value_type.__convert__(v, value_sub, state),
                    )
                    for k, v in dct.items()
                ]
            )
        except errors.ConversionError as e:
            raise errors.ConversionError(
                value,
                f"{value} is not a valid {typ.name} of "
                f"{key_sub.name} keys and {value_sub.name} values",
                source=e,
            ) from e


# Typing types ---------------------------------------------------------------------------------


class UnionAlias(Alias, of=t.Union):
    @classmethod
    def g_convert(cls, value: t.Any, info: TypeInfo, state):

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


class LiteralAlias(Alias, of=t.Literal):
    @classmethod
    def g_convert(cls, value: t.Any, info: TypeInfo):
        for sub in info.sub_types:
            if str(sub.base) == value:
                return sub.base

        raise errors.ConversionError(
            value, f"must be {join_or(list(sub.base for sub in info.sub_types))}"
        )


# Stdlib types ---------------------------------------------------------------------------------


class EnumAlias(Alias, of=enum.Enum):
    @classmethod
    def convert(cls, value: t.Any, info: TypeInfo[enum.Enum]):
        try:
            if issubclass(info.origin, enum.IntEnum):
                return info.origin(int(value))

            return info.origin(value)
        except ValueError as e:
            raise errors.ConversionError(
                value,
                f"must be {join_or([m.value for m in info.origin.__members__.values()])}",
            ) from e


class PathAlias(Alias, of=pathlib.Path):
    @classmethod
    def convert(cls, value: t.Any):
        return pathlib.Path(value)


class IOAlias(Alias, of=(_io._IOBase, t.IO)):
    @classmethod
    def convert(cls, value: str, info: TypeInfo) -> t.IO:
        try:
            file: t.IO = open(value, **cls.open_args(info))
            return file
        except FileNotFoundError as e:
            raise errors.ConversionError(value, f"No file named {value}") from e

    @classmethod
    def open_args(cls, info):
        arg = info.annotations[0]
        if isinstance(arg, str):
            return {"mode": arg}
        if dataclasses.is_dataclass(arg):
            return dataclasses.asdict(arg)


class _Address(Alias):
    alias_for: t.ClassVar[type]

    @classmethod
    def convert(cls, value: str, info):
        try:
            return cls.alias_for(value)
        except ipaddress.AddressValueError as e:
            raise errors.ConversionError(
                value, f"Not a valid {info.name} Address"
            ) from e


class IPv4Alias(_Address, of=ipaddress.IPv4Address):
    name = "IPv4"


class IPv6Alias(_Address, of=ipaddress.IPv6Address):
    name = "IPv6"
