import typing as t
from arc.types.params import as_special_param

T = t.TypeVar("T")


@as_special_param()
class VarPositional(list[T]):
    ...


@as_special_param()
class VarKeyword(dict[str, T]):
    ...
