from __future__ import annotations

import types
import typing as t
from functools import cached_property
from arc.constants import COLLECTION_TYPES

import arc.typing as at
from arc.types.aliases import Alias
from arc.types.type_arg import TypeArg

T = t.TypeVar("T")


class TypeInfo(t.Generic[T]):
    def __init__(
        self,
        original_type: at.Annotation,
        origin: type[T],
        sub_types: tuple[TypeInfo[t.Any], ...],
        annotations: tuple[t.Any, ...],
        name: str | None = None,
    ):
        self.original_type = original_type
        self.origin: t.Any = origin
        self.sub_types = sub_types
        self.annotations = annotations
        self.name = (
            name
            or getattr(self.origin, "name", None)
            or getattr(self.origin, "__name__", None)
            or str(self.origin)
        )

    @cached_property
    def type_arg(self) -> TypeArg | None:
        args = (a for a in self.annotations if isinstance(a, TypeArg))
        try:
            curr = next(args)
        except StopIteration:
            return None

        for arg in args:
            curr |= arg
        return curr

    @cached_property
    def middleware(self) -> list[at.TypeMiddleware]:
        return [a for a in self.annotations if callable(a)]

    @cached_property
    def resolved_type(self) -> type[at.TypeProtocol]:
        return Alias.resolve(self.origin)

    @property
    def is_union_type(self) -> bool:
        """The type is `Union[T...]`"""
        return self.origin in (t.Union, types.UnionType)

    @property
    def is_optional_type(self) -> bool:
        """The type is `Optional[T]`"""
        return (
            self.origin in (t.Union, types.UnionType)
            and len(self.sub_types) == 2
            and self.sub_types[-1].original_type is type(None)
        )

    @property
    def is_collection_type(self) -> bool:
        return self.origin in COLLECTION_TYPES

    @classmethod
    def analyze(cls, annotation: at.Annotation) -> TypeInfo[T]:
        """Create a `TypeInfo` object based on a type annotation"""
        original_type = annotation
        origin = t.get_origin(annotation) or annotation
        annotated_args: tuple[t.Any, ...] = tuple()

        if origin is t.Annotated:
            args = t.get_args(annotation)
            annotation = args[0]
            origin = t.get_origin(annotation) or annotation
            annotated_args = args[1:]

        sub_types = tuple(cls.analyze(arg) for arg in t.get_args(annotation))

        return cls(
            original_type=original_type,
            origin=origin,  # type: ignore
            sub_types=sub_types,
            annotations=annotated_args,
        )
