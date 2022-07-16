from __future__ import annotations
from typing import (
    Union,
    Any,
    TYPE_CHECKING,
)

from arc import utils

if TYPE_CHECKING:
    from arc.types.type_info import TypeInfo
    from arc.types.aliases import TypeProtocol
    from arc.context import Context


def convert_type(
    protocol: type[TypeProtocol],
    value: Any,
    info: TypeInfo,
    ctx: Context,
):
    """Uses `protocol` to convert `value`"""
    return utils.dispatch_args(protocol.__convert__, value, info, ctx)


def safe_issubclass(typ, classes: Union[type, tuple[type, ...]]) -> bool:
    try:
        return issubclass(typ, classes)
    except TypeError:
        return False


def iscontextmanager(obj: Any) -> bool:
    return hasattr(obj, "__enter__") and hasattr(obj, "__exit__")
