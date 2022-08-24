from __future__ import annotations
from functools import cached_property
import types
import typing as t
from arc.types.aliases import Alias
from arc.types.type_arg import TypeArg

import arc.typing as at
from arc.utils import safe_issubclass


T = t.TypeVar("T")


class TypeInfo(t.Generic[T]):
    def __init__(
        self,
        original_type: at.Annotation,
        origin: type[T],
        sub_types: tuple[TypeInfo, ...],
        annotations: tuple[t.Any, ...],
        name: str | None = None,
    ):
        self.original_type = original_type
        self.origin = origin
        self.sub_types = sub_types
        self.annotations = annotations
        self.name = (
            name
            or getattr(self.origin, "name", None)
            or getattr(self.origin, "__name__", None)
            or str(self.origin)
        )

    @cached_property
    def type_arg(self):
        args = (a for a in self.annotations if isinstance(a, TypeArg))
        try:
            curr = next(args)
        except StopIteration:
            return None

        for arg in args:
            curr |= arg
        return curr

    @cached_property
    def middleware(self) -> list[at.MiddlewareCallable]:
        return [a for a in self.annotations if callable(a)]

    @cached_property
    def resolved_type(self):
        return Alias.resolve(self.origin)

    @property
    def is_union_type(self) -> bool:
        """The type is `Union[T...]`"""
        return self.origin in (t.Union, types.UnionType)  # type: ignore

    @property
    def is_optional_type(self) -> bool:
        """The type is `Optional[T]`"""
        return (
            self.origin in (t.Union, types.UnionType)  # type: ignore
            and len(self.sub_types) == 2
            and self.sub_types[-1].original_type is type(None)
        )

    @classmethod
    def analyze(cls, annotation) -> TypeInfo:
        original_type = annotation
        origin = t.get_origin(annotation) or annotation
        annotated_args: tuple = tuple()

        if origin is t.Annotated:
            args = t.get_args(annotation)
            annotation = args[0]
            origin = t.get_origin(annotation) or annotation
            annotated_args = args[1:]

        sub_types = tuple(cls.analyze(arg) for arg in t.get_args(annotation))

        return cls(
            original_type=original_type,
            origin=origin,
            sub_types=sub_types,
            annotations=annotated_args,
        )
