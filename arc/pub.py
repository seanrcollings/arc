from __future__ import annotations
import sys
import typing as t
import shutil
from arc.context import Context
from arc.types.type_info import TypeInfo
from arc.types.helpers import convert_type
from arc.errors import ArcError
from arc.utils import ansi_clean


def convert(value: str, type: type, context: Context | None = None):
    try:
        context = context or Context.current()
    except ArcError:
        context = None

    info = TypeInfo.analyze(type)
    converted = convert_type(info.resolved_type, value, info, context)  # type: ignore

    for middleware in info.middleware:
        converted = middleware(converted)

    return converted


print()

T = t.TypeVar("T", contravariant=True)


class PrintProtocol(t.Protocol[T]):
    def write(self, __s: T) -> object:
        ...

    def isatty(self) -> bool:
        ...


def arc_print(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    file: PrintProtocol[str] = sys.stdout,
    flush: bool = False
):

    if not file.isatty():
        values = tuple(ansi_clean(str(v)) for v in values)

    print(*values, sep=sep, end=end, file=file, flush=flush)
