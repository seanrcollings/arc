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
from arc.types.helpers import (
    TypeInfo,
    join_and,
    join_or,
    match,
    safe_issubclass,
    convert,
    validate,
)

from arc.typing import Annotation, TypeProtocol

if t.TYPE_CHECKING:
    from arc.context import Context


logger = logging.getArcLogger("ali")


AliasFor = t.Union[Annotation, t.Tuple[Annotation, ...]]


class Alias:
    """Parent class for all aliases. Stores references to all
    known alias types and handles resolving them. Additionally,
    it provides a convenience wrapper for alias types by implementing
    a custom `cls.__convert__()` that calls `cls.convert()` for non-parameterized
    types and `cls.g_convert()` for generic types.
    """

    aliases: dict[Annotation, type[TypeProtocol]] = {}
    alias_for: t.ClassVar[AliasFor] = None  # type: ignore
    name: t.ClassVar[t.Optional[str]] = None
    convert: t.Callable
    g_convert: t.Callable

    @classmethod
    def __convert__(cls, value, typ: TypeInfo, ctx: Context):
        if cls.name:
            typ._name = cls.name

        if not typ.sub_types:
            obj = utils.dispatch_args(cls.convert, value, typ, ctx)
        else:
            obj = utils.dispatch_args(cls.g_convert, value, typ, ctx)

        # Alias types that have an associated "strict" type
        # will always return an instance of themselves, so all
        # validations will execute. For the alias itself, we just
        # want to return the type it aliases, so we convert it
        # back to that type
        if isinstance(obj, cls):
            obj = cls.alias_for(obj)  # type: ignore # pylint: disable=not-callable

        return obj

    def __init_subclass__(cls, of: t.Optional[AliasFor] = None):
        if of:
            cls.alias_for = of

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
        raise errors.ArgumentError(
            f"{name} is not a valid type. "
            f"Please ensure that {name} conforms to the custom type protocol "
            f"or that there is a alias type registered for it: "
            "<link stub>"
        )


# Builtin Types ---------------------------------------------------------------------------------


@validate
class StringAlias(Alias, str, of=str):
    max_length: t.ClassVar[t.Optional[int]] = None
    min_length: t.ClassVar[t.Optional[int]] = None
    length: t.ClassVar[t.Optional[int]] = None
    matches: t.ClassVar[t.Optional[str]] = None

    @classmethod
    def convert(cls, value: t.Any) -> str:
        try:
            return cls(value)  # type: ignore
        except ValueError as e:
            raise errors.ConversionError(value, str(e)) from e

    def _validate(self):
        if self.max_length and len(self) > self.max_length:
            raise ValueError(f"maximum length is {self.max_length}")

        if self.min_length and len(self) < self.min_length:
            raise ValueError(f"minimum length is {self.min_length}")

        if self.length and len(self) != self.length:
            raise ValueError(f"must be {self.length} characters long")

        if self.matches and (err := match(self.matches, self)).err:
            raise ValueError(err.unwrap())


class BytesAlias(bytes, Alias, of=bytes):
    @classmethod
    def convert(cls, value: t.Any) -> bytes:
        return str(value).encode()


class _NumberBaseAlias(Alias):
    alias_for: t.ClassVar[type]
    greater_than: t.ClassVar[t.Union[int, float]] = float("-inf")
    less_than: t.ClassVar[t.Union[int, float]] = float("inf")
    matches: t.ClassVar[t.Optional[str]] = None

    @classmethod
    def convert(cls, value: t.Any) -> t.Any:
        try:
            converted = cls(value)  # type: ignore
        except ValueError as e:
            raise errors.ConversionError(value, "invalid value", str(e)) from e

        return converted

    def _validate_shared(self):
        if self > self.less_than:
            raise ValueError(f"must be less than {self.less_than}")
        if self < self.greater_than:
            raise ValueError(f"must be greater than {self.greater_than}")

        if self.matches:
            if (err := match(self.matches, str(self))).err:
                raise ValueError(str(err))


@validate
class IntAlias(int, _NumberBaseAlias, of=int):
    name = "integer"
    base: t.ClassVar[int] = 10

    def __new__(cls, value: t.Any):
        if isinstance(value, str):
            return int.__new__(cls, value, base=cls.base)
        else:
            return int.__new__(cls, value)


@validate
class FloatAlias(float, _NumberBaseAlias, of=float):
    name = "float"
    min_precision: t.ClassVar[t.Optional[int]] = None
    max_precision: t.ClassVar[t.Optional[int]] = None
    precision: t.ClassVar[t.Optional[int]] = None

    def _validate(self):
        _natural, fractional = str(self).split(".")

        if self.min_precision and self.min_precision > len(fractional):
            raise ValueError(
                f"minimum decimal precision allowed is {self.min_precision}"
            )

        if self.max_precision and self.max_precision < len(fractional):
            raise ValueError(
                f"maximum decimal precision allowed is {self.min_precision}"
            )

        if self.precision and self.precision != len(fractional):
            raise ValueError(f"decimal precision must be {self.precision}")


TRUE_VALUES = {"true", "t", "yes", "1"}
FALSE_VALUES = {"false", "f", "no", "0"}


class BoolAlias(int, Alias, of=bool):
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
    def convert(cls, value: t.Any):
        if isinstance(value, str):
            return cls.alias_for(value.split(","))
        elif isinstance(value, list):
            return cls.alias_for(value)

    @classmethod
    def g_convert(cls, value: str, typ: TypeInfo, ctx):
        lst = cls.convert(value)
        sub = typ.sub_types[0]
        sub_type = Alias.resolve(sub)

        try:
            return cls.alias_for([sub_type.__convert__(v, sub, ctx) for v in lst])
        except errors.ConversionError as e:
            raise errors.ConversionError(
                value,
                f"{value} is not a valid {typ.name} of {sub.name}s",
            ) from e


class ListAlias(list, _CollectionAlias, of=list):
    ...


class SetAlias(set, _CollectionAlias, of=set):
    ...


class TupleAlias(tuple, _CollectionAlias, of=tuple):
    @classmethod
    def g_convert(cls, value: str, info: TypeInfo, ctx: Context):
        tup = cls.convert(value)

        # Arbitraryily sized tuples
        if cls.any_size(info):
            return super().g_convert(value, info, ctx)

        # Statically sized tuples
        if len(info.sub_types) != len(tup):

            raise errors.ConversionError(
                value,
                f"accepts {len(info.sub_types)} arguments, but recieved {len(tup)}",
            )

        return tuple(
            convert(Alias.resolve(item_type), item, item_type, ctx)
            for item_type, item in zip(info.sub_types, tup)
        )

    @classmethod
    def any_size(cls, info: TypeInfo):
        return info.sub_types[-1].origin is Ellipsis


class DictAlias(dict, Alias, of=dict):
    alias_for: t.ClassVar[type]
    name = "dictionary"

    @classmethod
    def convert(cls, value: str, info: TypeInfo, ctx):
        dct = cls.alias_for(i.split("=") for i in value.split(","))
        if isinstance(info.origin, t._TypedDictMeta):  # type: ignore
            return cls.__typed_dict_convert(dct, info, ctx)

        return dct

    @classmethod
    def g_convert(cls, value, info: TypeInfo, ctx):
        dct: dict = cls.convert(value, info, ctx)
        key_sub = info.sub_types[0]
        key_type = Alias.resolve(key_sub)
        value_sub = info.sub_types[1]
        value_type = Alias.resolve(value_sub)

        try:
            return cls.alias_for(
                [
                    (
                        convert(key_type, k, key_sub, ctx),
                        convert(value_type, v, value_sub, ctx),
                    )
                    for k, v in dct.items()
                ]
            )
        except errors.ConversionError as e:
            raise errors.ConversionError(
                value,
                f"{value} is not a valid {info.name} of "
                f"{key_sub.name} keys and {value_sub.name} values",
                source=e,
            ) from e

    @classmethod
    def __typed_dict_convert(cls, elements: dict[str, str], info: TypeInfo, ctx):
        hints = t.get_type_hints(info.origin, include_extras=True)
        for key, value in elements.items():
            if key not in hints:
                raise errors.ConversionError(
                    elements,
                    f"{key} is not a valid key name. "
                    f"Valid keys are: {join_and(list(hints.keys()))}",
                )

            sub_type = Alias.resolve(hints[key])
            try:
                elements[key] = convert(sub_type, value, info, ctx)
            except errors.ConversionError as e:
                raise errors.ConversionError(
                    value, f"{value} is not a valid value for key {key}", e
                ) from e

        return elements


# Typing types ---------------------------------------------------------------------------------


class UnionAlias(Alias, of=t.Union):
    @classmethod
    def g_convert(cls, value: t.Any, info: TypeInfo, ctx):

        for sub in info.sub_types:
            try:
                type_cls = Alias.resolve(sub)
                return convert(type_cls, value, sub, ctx)
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
            if value.isnumeric():
                return cls.alias_for(int(value))

            return cls.alias_for(value)
        except ipaddress.AddressValueError as e:
            raise errors.ConversionError(
                value, f"Not a valid {info.name} Address"
            ) from e


class IPv4Alias(ipaddress.IPv4Address, _Address, of=ipaddress.IPv4Address):
    name = "IPv4"


class IPv6Alias(ipaddress.IPv4Address, _Address, of=ipaddress.IPv6Address):
    name = "IPv6"
