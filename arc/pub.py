from arc.context import Context
from arc.types.type_info import TypeInfo
from arc.types.helpers import convert_type
from arc import errors


def convert(value: str, type: type, context: Context | None = None):
    try:
        context = context or Context.current()
    except errors.ArcError:
        context = None

    info = TypeInfo.analyze(type)
    converted = convert_type(info.resolved_type, value, info, context)  # type: ignore

    for transform in info.transforms:
        converted = transform(converted)

    return converted


def print():
    ...
