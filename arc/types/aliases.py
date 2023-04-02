"""Module for all Alias types. Alias types are types that handle to conversion for other types.
All builtin types (int, str, float, etc...) have a corresponding Alias type.
"""
from __future__ import annotations

import collections
import enum
import ipaddress
import pathlib
import re
import types
import typing as t

import _io  # type: ignore

from arc import api, autocompletions, errors, safe
from arc.autocompletions import Completion, CompletionInfo, CompletionType
from arc.color import colorize, fg
from arc.present.joiner import Join
from arc.prompt.prompts import select_prompt
from arc.types.convert import convert_type
from arc.types.type_arg import TypeArg
from arc.typing import Annotation, TypeProtocol

if t.TYPE_CHECKING:
    from arc.define.param import Param
    from arc.runtime import Context
    from arc.types.type_info import TypeInfo


AliasFor = t.Union[Annotation, t.Tuple[Annotation, ...]]

T = t.TypeVar("T")


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
    convert: t.Callable[..., t.Any]
    g_convert: t.Callable[..., t.Any]

    @classmethod
    def __convert__(cls, value: str, typ: TypeInfo[T]) -> T:
        if cls.name:
            typ.name = cls.name

        if not typ.sub_types:
            obj = api.dispatch_args(cls.convert, value, typ)
        else:
            obj = api.dispatch_args(cls.g_convert, value, typ)

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

        if safe.issubclass(annotation, TypeProtocol):
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
        raise TypeError(
            f"{name} is not a valid type. "
            f"Please ensure that {name} conforms to the custom type protocol "
            f"or that there is a alias type registered for it: "
            "https://arc.seancollings.dev/usage/parameters/types/custom-types"
        )


# Builtin Types ---------------------------------------------------------------------------------


class StringAlias(Alias, str, of=(str, t.Any, collections.UserString)):  # type: ignore
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
    def convert(cls, value: str, info: TypeInfo[float]) -> float:
        try:
            return info.origin(value)
        except ValueError as e:
            raise errors.ConversionError(value, "must be a float", e)


class _CollectionAlias(Alias):
    alias_for: t.ClassVar[type]

    @classmethod
    def convert(cls, value: t.Any) -> t.Any:
        if isinstance(value, str):
            return cls.alias_for(value.split(","))
        return cls.alias_for(value)

    @classmethod
    def g_convert(cls, value: str, typ: TypeInfo[t.Any]) -> t.Any:
        lst = cls.convert(value)
        sub = typ.sub_types[0]
        sub_type = sub.resolved_type

        try:
            return cls.alias_for([sub_type.__convert__(v, sub) for v in lst])
        except errors.ConversionError as e:
            if name := getattr(sub_type, "name"):
                raise errors.ConversionError(
                    value,
                    f"{colorize(' '.join(value), fg.YELLOW)} is not a valid {typ.name} of {name}s",
                    e,
                ) from e
            raise e


class ListAlias(list[t.Any], _CollectionAlias, of=list):
    ...


class SetAlias(set[t.Any], _CollectionAlias, of=set):
    ...


class TupleAlias(tuple[t.Any], _CollectionAlias, of=tuple):
    @classmethod
    def g_convert(cls, value: str, info: TypeInfo[T]) -> tuple[t.Any, ...]:
        tup = cls.convert(value)

        # Arbitraryily sized tuples
        if cls.any_size(info):
            return super().g_convert(value, info)

        # Statically sized tuples
        if len(info.sub_types) != len(tup):

            raise errors.ConversionError(
                value,
                f"accepts {len(info.sub_types)} arguments, but recieved {len(tup)}",
            )

        return tuple(
            convert_type(item_type.resolved_type, item, item_type)
            for item_type, item in zip(info.sub_types, tup)
        )

    @classmethod
    def any_size(cls, info: TypeInfo[T]) -> bool:
        return info.sub_types[-1].origin is Ellipsis


class DictAlias(dict[str, t.Any], Alias, of=dict):
    alias_for: t.ClassVar[type]

    @classmethod
    def convert(cls, value: str, info: TypeInfo[t.Any]) -> dict[str, str]:
        dct = cls.alias_for(i.split("=") for i in value.split(","))
        if isinstance(info.origin, t._TypedDictMeta):  # type: ignore
            return cls.__typed_dict_convert(dct, info)

        return dct

    @classmethod
    def g_convert(cls, value: str, info: TypeInfo[t.Any]) -> dict[str, t.Any]:
        dct: dict[str, t.Any] = cls.convert(value, info)
        key_sub = info.sub_types[0]
        key_type = key_sub.resolved_type
        value_sub = info.sub_types[1]
        value_type = value_sub.resolved_type

        try:
            return cls.alias_for(
                [
                    (
                        convert_type(key_type, k, key_sub),
                        convert_type(value_type, v, value_sub),
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
    def __typed_dict_convert(
        cls, elements: dict[str, str], info: TypeInfo[t.Any]
    ) -> dict[str, t.Any]:
        hints = t.get_type_hints(info.origin, include_extras=True)
        for key, value in elements.items():
            if key not in hints:
                raise errors.ConversionError(
                    elements,
                    f"{key} is not a valid key name. "
                    f"Valid keys are: {Join.with_and(list(hints.keys()))}",
                )

            sub_info = type(info).analyze(hints[key])
            try:
                elements[key] = convert_type(sub_info.resolved_type, value, sub_info)
            except errors.ConversionError as e:
                raise errors.ConversionError(
                    value, f"{value} is not a valid value for key {key}", e
                ) from e

        return elements


class NoneAlias(Alias, of=types.NoneType):
    @classmethod
    def convert(self, value: t.Any) -> t.NoReturn:
        raise errors.ConversionError(value, "")


# Typing types ---------------------------------------------------------------------------------


class UnionAlias(Alias, of=(t.Union, types.UnionType)):
    @classmethod
    def g_convert(cls, value: t.Any, info: TypeInfo[t.Any]) -> t.Any:

        for sub in info.sub_types:
            try:
                return convert_type(sub.resolved_type, value, sub)
            except Exception:
                ...

        options = Join.with_or(
            list(sub.name for sub in info.sub_types if sub.origin is not types.NoneType)
        )
        raise errors.ConversionError(
            value,
            f"must be a {options}",
        )


class LiteralAlias(Alias, of=t.Literal):
    @classmethod
    def g_convert(cls, value: t.Any, info: TypeInfo[t.Any]) -> t.Any:
        for sub in info.sub_types:
            if str(sub.original_type) == value:
                return sub.original_type

        raise errors.ConversionError(
            value,
            f"must be {Join.with_or(list(sub.original_type for sub in info.sub_types))}",
        )

    @classmethod
    def __prompt__(cls, param: Param[t.Any], ctx: Context) -> str:
        return select_prompt(
            ctx.prompt,
            t.cast(str, param.prompt),
            list(str(tp.origin) for tp in param.type.sub_types),
            highlight_color=ctx.config.present.color.accent,
        )

    @classmethod
    def __completions__(
        cls, info: CompletionInfo, param: Param[t.Any]
    ) -> t.Iterator[autocompletions.Completion]:
        for tp in param.type.sub_types:
            yield autocompletions.Completion(str(tp.origin))


# Stdlib types ---------------------------------------------------------------------------------


class EnumAlias(Alias, of=enum.Enum):
    @classmethod
    def convert(cls, value: t.Any, info: TypeInfo[enum.Enum]) -> t.Any:
        try:
            if issubclass(info.origin, enum.IntEnum):
                return info.origin(int(value))

            return info.origin(value)
        except ValueError as e:
            raise errors.ConversionError(
                value,
                f"must be {Join.with_or([m.value for m in info.origin.__members__.values()])}",
            ) from e

    @classmethod
    def __prompt__(cls, param: Param[enum.Enum], ctx: Context) -> t.Any:
        enum_cls: type[enum.Enum] = param.type.origin
        return select_prompt(
            ctx.prompt,
            t.cast(str, param.prompt),
            list(str(m.value) for m in enum_cls.__members__.values()),
            highlight_color=ctx.config.present.color.accent,
        )

    @classmethod
    def __completions__(
        cls, info: CompletionInfo, param: Param[enum.Enum]
    ) -> t.Iterator[autocompletions.Completion]:
        for m in param.type.origin.__members__.values():
            yield autocompletions.Completion(str(m.value))


class PathAlias(Alias, of=pathlib.Path):
    @classmethod
    def convert(cls, value: t.Any) -> pathlib.Path:
        return pathlib.Path(value)

    @classmethod
    def __completions__(
        cls, info: CompletionInfo, _param: Param[pathlib.Path]
    ) -> t.Iterator[Completion]:
        yield Completion(info.current, type=CompletionType.FILE)


class IOAlias(Alias, of=(_io._IOBase, t.IO)):
    name = "file"

    @classmethod
    def convert(cls, value: str, info: TypeInfo[t.Any]) -> t.IO[str]:
        error_msg = f"Cannot access {value}:"
        arg = TypeArg.ensure(info.type_arg, str(info.origin))
        try:
            file: t.IO[str] = open(value, **arg.dict())
            return file
        except FileNotFoundError as e:
            raise errors.ConversionError(value, f"{error_msg} file not found") from e
        except PermissionError as e:
            raise errors.ConversionError(value, f"{error_msg} permission denied") from e

    @classmethod
    def __completions__(
        cls, info: CompletionInfo, _param: Param[t.IO[str]]
    ) -> t.Iterator[Completion]:
        yield Completion(info.current, type=CompletionType.FILE)


class _Address(Alias):
    alias_for: t.ClassVar[type]

    @classmethod
    def convert(
        cls, value: str, info: TypeInfo[t.Any]
    ) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
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
    def convert(cls, value: str, info: TypeInfo[t.Any]) -> re.Pattern[str]:
        try:
            return re.compile(value, cls.flags(info))
        except re.error as e:
            raise errors.ConversionError(
                value, "Not a valid regular expression", e
            ) from e

    @classmethod
    def flags(cls, info: TypeInfo[t.Any]) -> int:
        if len(info.annotations) == 0:
            return 0
        return info.annotations[0]
