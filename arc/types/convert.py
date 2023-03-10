from __future__ import annotations

import typing as t

from arc import api, types

if t.TYPE_CHECKING:
    from arc.typing import TypeProtocol


def convert_type(
    protocol: type[TypeProtocol],
    value: t.Any,
    info: types.TypeInfo,
):
    """Uses `protocol` to convert `value`"""
    return api.dispatch_args(protocol.__convert__, value, info)


T = t.TypeVar("T")


def convert(value: str, type: type[T]) -> T:
    info = types.TypeInfo.analyze(type)
    converted = convert_type(info.resolved_type, value, info)

    for middleware in info.middleware:
        converted = api.dispatch_args(middleware, converted, None)

    return converted
