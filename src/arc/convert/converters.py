from typing import Dict, Type, Optional, Union, Any
from typing import _GenericAlias as GenericAlias  # type: ignore
from enum import Enum

from arc.types import ArcType
from arc.convert.base_converter import BaseConverter, TypeConverter
from arc.convert import ConversionError
from arc.errors import ArcError
from arc.types import File, Range


class StringConverter(TypeConverter, BaseConverter):
    convert_to = str


class IntConverter(BaseConverter):
    convert_to = int

    def convert(self, value):
        if value.isnumeric():
            return int(value)
        raise ConversionError(value, expected="a whole number integer")


class FloatConverter(BaseConverter):
    convert_to = float

    def convert(self, value):
        try:
            return float(value)
        except ValueError as e:
            raise ConversionError(value, expected="a float (1.3, 4, 1.7)") from e


class BytesConverter(BaseConverter):
    convert_to = bytes

    def convert(self, value):
        return value.encode()


class BoolConverter(BaseConverter):
    """Converts a string to a boolean
    True / true - True
    False / false - False
    """

    convert_to = bool

    def convert(self, value):
        if value.isnumeric():
            return bool(int(value))

        value = value.lower()
        if value in ("true", "t"):
            return True
        elif value in ("false", "f"):
            return False

        raise ConversionError(value, "'(t)rue' or '(f)alse' or a valid integer")


class IntBoolConverter(BaseConverter):
    """Converts an int to a boolean.
    0 - False
    All other ints / floats - True
    """

    convert_to = bool

    def convert(self, value):
        if value.isnumeric():
            value = int(value)
            return value != 0
        raise ConversionError(value, "ibool only accepts whole number integers")


class ListConverter(BaseConverter):
    """Converts arguement into an array
    argument: my_list=1,2,3,4,5,6
    return : ["1", "2", "3", "4", "5", "6"]
    """

    convert_to = list

    def convert(self, value: str):
        if "," in value:
            return value.replace(" ", "").split(",")
        raise ConversionError(value, "a comma seperated list of strings")


class FileConverter(BaseConverter):
    """Converts a string to a file handler object
    /path/to/a/file
    """

    convert_to = File

    def convert(self, value):
        return self.annotation(value, self.annotation.__args__).open()


class AliasConverter(BaseConverter):
    """
    convert string inputs into their appropriate types
    based on the type alias provided

    Union[int, str]

        - i: '1234'
        - o: 1234

        - i: 'hello'
        - o: 'hello'

    List[int]

        - i: '1,2,3,4,5,6'
        - o: [1, 2, 3, 4, 5, 6]
    """

    convert_to = Any

    def convert(self, value):
        return self.convert_alias(self.annotation, value)

    def convert_alias(self, alias: Type[GenericAlias], value: str) -> Any:
        if not is_alias(alias):
            raise ConversionError(None, "Provided alias must inherit from GenericAlias")

        origin: str = alias.__origin__
        if origin is Union:
            return self.convert_union(alias, value)
        elif origin is list:
            return self.convert_list(alias, value)
        elif origin is set:
            return self.convert_set(alias, value)
        elif origin is tuple:
            return self.convert_tuple(alias, value)
        else:
            raise ConversionError(
                value=None,
                expected="a valid type alias",
                helper_text=f"Type Alias for '{origin}' not supported",
            )

    def convert_union(self, alias, value):
        for union_type in alias.__args__:
            try:
                if is_alias(union_type):
                    return self.convert_alias(union_type, value)

                converter = get_converter(union_type.__name__)
                if converter:
                    return converter(alias).convert(value)
            except ConversionError:
                continue

        raise ConversionError(value, f"Failed to convert {alias}")

    def collection_setup(self, collection_alias, value):
        contains_type = collection_alias.__args__[0]
        if is_alias(contains_type):
            raise ConversionError(
                contains_type,
                "a valid alias type",
                helper_text="Arc only supports shallow Collection Type Aliases",
            )

        value = value.replace(" ", "")

        return value.split(","), get_converter(contains_type.__name__)

    def convert_list(self, alias, value):
        items, converter = self.collection_setup(alias, value)
        return list([converter(list).convert(item) for item in items])

    def convert_set(self, alias, value):
        items, converter = self.collection_setup(alias, value)
        return set(converter(set).convert(item) for item in items)

    def convert_tuple(self, alias, value):
        items, _ = self.collection_setup(alias, value)
        if (i_len := len(items)) != (a_len := len(alias.__args__)):
            raise ConversionError(
                value=items,
                expected=f"a tuple of {a_len} item(s), was {i_len} item(s)",
            )

        return tuple(
            get_converter(alias.__args__[idx].__name__)(tuple).convert(item)  # type: ignore
            for idx, item in enumerate(items)
        )


class EnumConverter(BaseConverter):
    convert_to = Enum

    def convert(self, value):
        if value.isnumeric():
            value = int(value)

        try:
            return self.annotation(value)
        except ValueError as e:
            raise ConversionError(
                value,
                expected=f"to be one of: {', '.join(str(data.value) for data in self.annotation)}",
            ) from e


class RangeConverter(BaseConverter):
    convert_to = Range
    _range: Optional[tuple[int, int]] = None

    def convert(self, value: str):
        error = ConversionError(
            value,
            f"an integer in range: {self.range}",
            "Note that the range is inclusive on the minimum and exclusive on the maximum",
        )

        if not value.isnumeric():
            raise error

        int_value = int(value)
        smallest, largest = self.range
        if not (int_value >= smallest and int_value < largest):
            raise error

        return Range(int_value, smallest, largest)

    @property
    def range(self):
        if self._range is None:
            smallest, largest = self.annotation.__args__
            if is_alias(smallest):
                smallest = smallest.__args__[0]
            if is_alias(largest):
                largest = largest.__args__[0]

            if isinstance(smallest, int) and isinstance(largest, int):
                self._range = smallest, largest
            else:
                raise ArcError(
                    f"The min and max of a range must be integers: {smallest, largest}"
                )

        return self._range


converter_mapping: Dict[str, Type[BaseConverter]] = {
    "str": StringConverter,
    "int": IntConverter,
    "float": FloatConverter,
    "bytes": BytesConverter,
    "bool": BoolConverter,
    "list": ListConverter,
    "alias": AliasConverter,
    "file": FileConverter,
    "range": RangeConverter,
    "enum": EnumConverter,
}


def get_converter(key: Union[str, type]) -> Optional[Type[BaseConverter]]:
    if isinstance(key, type):
        key = key.__name__
    return converter_mapping.get(key)


def is_alias(alias):
    return isinstance(alias, GenericAlias)


def is_enum(annotation: type):
    return Enum in annotation.mro()


def is_arc_type(annotation):
    if is_alias(annotation):
        return issubclass(annotation.__origin__, ArcType)

    return False
