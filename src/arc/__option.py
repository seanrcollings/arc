from typing import Type, Tuple, Any
from arc.config import Config
from arc.errors import ArcError
from arc.converter import is_converter, parse_converter, StringConverter, BaseConverter


class Option:
    def __init__(self, option: str):
        self.name, self.converter = self.parse(option)
        self.value: Any

    def __repr__(self):
        return f"<Option : {self.name}>"

    def convert(self):
        self.value = self.converter()._convert_wrapper(self.value)

    @staticmethod
    def parse(option: str) -> Tuple[str, Type[BaseConverter]]:
        """Parses provided option into name and converter

        Checks for a type converter
        :param options - array of strings. Can have a converter
            associated with it.
            - without converter "normal_string"
            - with converter "<int:number>"
        :returns: name of option, converter class
            StringConverter is default converter
        """
        name = option
        converter: Type[BaseConverter] = StringConverter

        if is_converter(option):
            name, converter_name = parse_converter(name)

            if converter_name not in Config.converters:
                raise ArcError(f"'{converter}' is not a valid", "conversion identifier")

            converter = Config.converters[converter_name]

        return name, converter
