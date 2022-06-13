from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property
import typing as t
from arc.types.aliases import Alias

import arc.typing as at


T = t.TypeVar("T")


@dataclass
class TypeInfo(t.Generic[T]):
    original_type: at.Annotation
    origin: type[T]
    sub_types: tuple[TypeInfo, ...]
    annotations: tuple[t.Any, ...]
    _name: str | None = None

    @property
    def name(self) -> str:
        return (
            self._name
            or getattr(self.origin, "name", None)
            or getattr(self.origin, "__name__", None)
            or str(self.origin)
        )

    @property
    def is_union_type(self) -> bool:
        """The type is `Union[T...]`"""
        return self.origin is t.Union

    @property
    def is_optional_type(self) -> bool:
        """The type is `Optional[T]`"""
        return (
            self.origin is t.Union
            and len(self.sub_types) == 2
            and self.sub_types[-1].original_type is type(None)
        )

    @cached_property
    def resolved_type(self):
        return Alias.resolve(self.origin)

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
