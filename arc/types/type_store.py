from typing import (
    _SpecialForm as SpecialForm,
    Union,
    TypedDict,
    Callable,
)
from arc import errors, types
from arc.color import fg, colorize

from .converters.base_converter import BaseConverter


TypeKey = Union[type, SpecialForm, object]
DisplayName = Union[str, Callable[[type], str]]


class TypeValue(TypedDict):
    converter: type[BaseConverter]
    display_name: DisplayName


class TypeStore(dict[TypeKey, TypeValue]):
    def get(self, kind: TypeKey, default=None) -> TypeValue:
        # Unwrap to handle generic types (list[int])
        kind = types.unwrap(kind)

        # Type is a key
        # We perform this check once before hand
        # because some typing types don't have
        # the mro() method
        if kind in self:
            return self[kind]

        # Type is a subclass of a key
        for cls in kind.mro():
            if cls in self:
                return self[cls]

        return default

    def get_converter(self, kind: TypeKey) -> type[BaseConverter]:
        if val := self.get(kind):
            return val["converter"]

        raise errors.ArcError(f"No Converter found for {kind}")

    def get_display_name(self, kind: TypeKey):
        if val := self.get(kind):
            display_name = val["display_name"]

            if callable(display_name):
                return display_name(kind)  # type: ignore
            return display_name

        raise errors.ArcError(f"{kind} not registered to TypeStore")

    def register(
        self,
        kinds: Union[TypeKey, tuple[TypeKey, ...]],
        cls: type[BaseConverter],
        display_name: DisplayName = None,
    ):
        """Registers decorated `cls` as the converter for `kinds`"""

        if isinstance(kinds, tuple):
            name = display_name or ", ".join(str(kind) for kind in kinds)
            for kind in kinds:
                self[kind] = {"converter": cls, "display_name": name}
        else:
            name = display_name or str(kinds)
            self[kinds] = {"converter": cls, "display_name": name}

        return cls


def register(
    kinds: Union[TypeKey, tuple[TypeKey, ...]],
    display_name: DisplayName = None,
):
    """Decorator wrapper around `type_store.register()`. Use to register a converter
    to one or more types. This can be used to register custom converters and types
    to arc.

    Args:
        kinds (Union[TypeKey, tuple[TypeKey, ...]]): Class(es) to register the
        decorated converter to
        display_name (Union[str, Callable[[type], str]], optional): A human-readable name
        for the given type. Can be a string, or a function that recieves the
        converter and returns a string. Defaults to None.

    Example:

    ```py
    from arc.types import register

    class CustomType():
        ...

    @register(CustomType, "custom-type")
    class CustomConverter(BaseConverter):
        def convert(self, value):
            ...
    ```
    """

    def wrapper(cls: type[BaseConverter]):
        return type_store.register(kinds, cls, display_name)

    return wrapper


def convert(value, kind, name: str = ""):
    """Converts the provided string to the provided type
    Args:
        value: value to convert
        kind: type to attempt the convertion to
        name: optional descriptive name of the argument
    """

    if not isinstance(value, str):
        return value

    converter_cls = type_store.get_converter(kind)
    converter = converter_cls(kind)

    try:
        value = converter.convert(value)
    except errors.ConversionError as e:
        raise errors.ArgumentError(
            f"Argument {colorize(name, fg.BLUE)} expected "
            f"{type_store.get_display_name(kind)}, but was "
            f"{colorize(value, fg.YELLOW)}. {e.helper_text}"
        ) from e

    return value


type_store = TypeStore()
