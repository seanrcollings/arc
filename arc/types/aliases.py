"""Module for all Alias types. Alias types are types that handle to conversion for other types.
All builtin types (int, str, float, etc...) have a corresponding Alias type.
"""
from __future__ import annotations

import enum
import pathlib
import types
import typing as t
import ipaddress
import dataclasses
import re

import _io  # type: ignore

from arc import errors, utils
from arc import autocompletions
from arc.autocompletions import Completion, CompletionInfo, CompletionType
from arc.color import colorize, fg
from arc.present.helpers import Joiner
from arc.types.helpers import (
    safe_issubclass,
    convert_type,
)
from arc.prompt.prompts import select_prompt


from arc.typing import Annotation, TypeProtocol

from arc.types import type_info

if t.TYPE_CHECKING:
    from arc.types.type_info import TypeInfo
    from arc.context import Context


AliasFor = t.Union[Annotation, t.Tuple[Annotation, ...]]


class Alias:
    """Parent class for all aliases. Stores references to all
    known alias types and handles resolving them. Additionally,
    it provides a convenience wrapper for alias types by implementing
    a custom `cls.__convert__()` that calls `cls.convert()` for non-parameterized
    types and `cls.g_convert()` for generic types.
    """

    aliases: dict[Annotation, type[TypeProtocol]] = {}
    alias_for: t.ClassVar[AliasFor | tuple[AliasFor]] = None  # type: ignore
    name: t.ClassVar[t.Optional[str]] = None
    convert: t.Callable
    g_convert: t.Callable

    @classmethod
    def __convert__(cls, value, typ: TypeInfo, ctx: Context):
        if cls.name:
            typ.name = cls.name

        if not typ.sub_types:
            obj = utils.dispatch_args(cls.convert, value, typ, ctx)
        else:
            obj = utils.dispatch_args(cls.g_convert, value, typ, ctx)

        return obj

    def __init_subclass__(cls, of: t.Optional[AliasFor | tuple[AliasFor]] = None):
        if of:
            cls.alias_for = of

            if isinstance(cls.alias_for, tuple):
                aliases = cls.alias_for
            else:
                aliases = (cls.alias_for,)

            for alias in aliases:
                Alias.aliases[alias] = cls  # type: ignore

    @classmethod
    def resolve(cls, annotation: type) -> type[TypeProtocol]:
        """Handles resolving alias types"""

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
        raise errors.ParamError(
            f"{name} is not a valid type. "
            f"Please ensure that {name} conforms to the custom type protocol "
            f"or that there is a alias type registered for it: "
            "https://arc.seanrcollings.com/usage/parameter-types/#custom-types"
        )


# Builtin Types ---------------------------------------------------------------------------------


class StringAlias(Alias, str, of=str):
    @classmethod
    def convert(cls, value: str, info: TypeInfo[str]) -> str:
        try:
            return str(value)
        except ValueError as e:
            raise errors.ConversionError(value, str(e))


class BytesAlias(bytes, Alias, of=bytes):
    @classmethod
    def convert(cls, value: t.Any) -> bytes:
        return str(value).encode()


class IntAlias(Alias, of=int):
    @classmethod
    def convert(cls, value: str, info: TypeInfo[int]) -> int:
        args = info.type_arg
        try:
            if isinstance(value, str):
                params = args.dict() if args else {}
                return int(value, **params)
            else:
                return int(value)
        except ValueError as e:
            raise errors.ConversionError(value, "must be an integer", e)


class FloatAlias(Alias, of=float):
    @classmethod
    def convert(cls, value, info: TypeInfo[float]) -> float:
        try:
            return info.origin(value)
        except ValueError as e:
            raise errors.ConversionError(value, "must be a float", e)


class _CollectionAlias(Alias):
    alias_for: t.ClassVar[type]

    @classmethod
    def convert(cls, value: t.Any):
        if isinstance(value, str):
            return cls.alias_for(value.split(","))
        return cls.alias_for(value)

    @classmethod
    def g_convert(cls, value: str, typ: TypeInfo, ctx):
        lst = cls.convert(value)
        sub = typ.sub_types[0]
        sub_type = sub.resolved_type

        try:
            return cls.alias_for([sub_type.__convert__(v, sub, ctx) for v in lst])
        except errors.ConversionError as e:
            if name := getattr(sub_type, "name"):
                raise errors.ConversionError(
                    value,
                    f"{colorize(' '.join(value), fg.YELLOW)} is not a valid {typ.name} of {name}s",
                    e,
                ) from e
            raise e


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
            convert_type(item_type.resolved_type, item, item_type, ctx)
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
        key_type = key_sub.resolved_type
        value_sub = info.sub_types[1]
        value_type = value_sub.resolved_type

        try:
            return cls.alias_for(
                [
                    (
                        convert_type(key_type, k, key_sub, ctx),
                        convert_type(value_type, v, value_sub, ctx),
                    )
                    for k, v in dct.items()
                ]
            )
        except errors.ConversionError as e:
            raise errors.ConversionError(
                value,
                f"{value} is not a valid {info.name} of "
                f"{key_sub.name} keys and {value_sub.name} values",
                e,
            ) from e

    @classmethod
    def __typed_dict_convert(cls, elements: dict[str, str], info: TypeInfo, ctx):
        hints = t.get_type_hints(info.origin, include_extras=True)
        for key, value in elements.items():
            if key not in hints:
                raise errors.ConversionError(
                    elements,
                    f"{key} is not a valid key name. "
                    f"Valid keys are: {Joiner.with_and(list(hints.keys()))}",
                )

            sub_info = type_info.TypeInfo.analyze(hints[key])
            try:
                elements[key] = convert_type(
                    sub_info.resolved_type, value, sub_info, ctx
                )
            except errors.ConversionError as e:
                raise errors.ConversionError(
                    value, f"{value} is not a valid value for key {key}", e
                ) from e

        return elements


class NoneAlias(Alias, of=types.NoneType):
    @classmethod
    def convert(self, value: t.Any):
        raise errors.ConversionError(value, "")


# Typing types ---------------------------------------------------------------------------------


class UnionAlias(Alias, of=(t.Union, types.UnionType)):  # type: ignore
    @classmethod
    def g_convert(cls, value: t.Any, info: TypeInfo, ctx):

        for sub in info.sub_types:
            try:
                return convert_type(sub.resolved_type, value, sub, ctx)
            except Exception:
                ...

        options = Joiner.with_or(
            list(sub.name for sub in info.sub_types if sub.origin is not types.NoneType)
        )
        raise errors.ConversionError(
            value,
            f"must be a {options}",
        )


class LiteralAlias(Alias, of=t.Literal):
    @classmethod
    def g_convert(cls, value: t.Any, info: TypeInfo):
        for sub in info.sub_types:
            if str(sub.original_type) == value:
                return sub.original_type

        raise errors.ConversionError(
            value,
            f"must be {Joiner.with_or(list(sub.original_type for sub in info.sub_types))}",
        )

    @classmethod
    def __prompt__(cls, ctx, param):
        return select_prompt(
            list(str(tp.origin) for tp in param.type.sub_types), ctx, param
        )

    @classmethod
    def __completions__(cls, info, param):
        return [
            autocompletions.Completion(str(tp.origin)) for tp in param.type.sub_types
        ]


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
                f"must be {Joiner.with_or([m.value for m in info.origin.__members__.values()])}",
            ) from e

    @classmethod
    def __prompt__(cls, ctx, param):
        return select_prompt(
            list(str(m.value) for m in param.type_info.origin.__members__.values()),
            ctx,
            param,
        )

    @classmethod
    def __completions__(cls, info, param):
        return [
            autocompletions.Completion(str(m.value))
            for m in param.type_info.origin.__members__.values()
        ]


class PathAlias(Alias, of=pathlib.Path):
    @classmethod
    def convert(cls, value: t.Any):
        return pathlib.Path(value)


class IOAlias(Alias, of=(_io._IOBase, t.IO)):
    name = "file"

    @classmethod
    def convert(cls, value: str, info: TypeInfo) -> t.IO:
        try:
            file: t.IO = open(value, **info.type_arg.dict())
            return file
        except FileNotFoundError as e:
            raise errors.ConversionError(value, f"No file named {value}") from e

    @classmethod
    def __completions__(cls, info: CompletionInfo, _param):
        return Completion(info.current, CompletionType.FILE)


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


class IPv6Alias(ipaddress.IPv6Address, _Address, of=ipaddress.IPv6Address):
    name = "IPv6"


class PatternAlias(Alias, of=re.Pattern):
    @classmethod
    def convert(cls, value: str, info: TypeInfo):
        try:
            return re.compile(value, cls.flags(info))
        except re.error as e:
            raise errors.ConversionError(
                value, "Not a valid regular expression", e
            ) from e

    @classmethod
    def flags(cls, info: TypeInfo):
        if len(info.annotations) == 0:
            return 0
        return info.annotations[0]
