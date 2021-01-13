from typing import Dict, Type, Optional, Union, Any
from typing import _GenericAlias as GenericAlias  # type: ignore

from arc.convert.base_converter import BaseConverter
from arc.convert import ConversionError
from arc.types.file import File


class StringConverter(BaseConverter):
    convert_to = str


class IntConverter(BaseConverter):
    convert_to = int

    def convert(self, value):
        if value.isnumeric():
            return int(value)
        raise ConversionError(value, "Value must be a whole number integer")


class FloatConverter(BaseConverter):
    convert_to = float

    def convert(self, value):
        try:
            return float(value)
        except ValueError as e:
            raise ConversionError(value, "Value must be a number (1.3, 4, 1.7)") from e


class BytesConverter(BaseConverter):
    convert_to = bytes

    def convert(self, value):
        return value.encode()


# !! DEPRECATED !!
# Honestly, I don't think these will ever get called
# Since bool annotations get matched with flags and not options
class BoolConverter(BaseConverter):
    convert_to = bool


class StringBoolConverter(BaseConverter):
    """Converts a string to a boolean
    True / true - True
    False / false - False
    """

    convert_to = bool

    def convert(self, value):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False

        raise ConversionError(value, "sbool only accepts true or false")


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

    def convert(self, value):
        if "," in value:
            return value.replace(" ", "").split(",")
        raise ConversionError(
            value, "ListConverter only accepts comma seperated strings"
        )


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

        - i: '1,2,3,4,5,6's
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
            raise ConversionError(None, f"Type Alias for '{origin}' not supported")

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
                message="Arc only supports shallow Collection Type Aliases",
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
                value=items, message=f"{alias} expects {a_len} item(s), was {i_len}",
            )

        return tuple(
            get_converter(alias.__args__[idx].__name__)(tuple).convert_wrapper(item)  # type: ignore
            for idx, item in enumerate(items)
        )


converter_mapping: Dict[str, Type[BaseConverter]] = {
    "str": StringConverter,
    "int": IntConverter,
    "float": FloatConverter,
    "bytes": BytesConverter,
    "bool": BoolConverter,
    "sbool": StringBoolConverter,
    "ibool": IntBoolConverter,
    "list": ListConverter,
    "alias": AliasConverter,
    "file": FileConverter,
}


def get_converter(key: Union[str, type]) -> Optional[Type[BaseConverter]]:
    if isinstance(key, type):
        key = key.__name__
    return converter_mapping.get(key)


def is_alias(alias):
    return isinstance(alias, GenericAlias)
