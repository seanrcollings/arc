from typing import Type
from arc.config import Config
from arc.errors import ArcError
from arc.converter import BaseConverter


class NoDefault:
    """Type for when a paramater doesn't have a default value"""


class Option:
    def __init__(self, param):
        self.name = param.name

        if param.annotation == param.empty:
            annotation = "str"
        else:
            annotation = param.annotation.__name__

        self.converter = self.get_converter(annotation)

        if param.default == param.empty:
            self.default = NoDefault
        else:
            self.default = param.default

        self.value = self.default

    def __repr__(self):
        return f"<Option : {self.name}>"

    def convert(self):
        # Consider removing the converter_wrapper and simply catching the error in here?
        self.value = self.converter().convert_wrapper(self.value)

    @staticmethod
    def get_converter(annotation: str) -> Type[BaseConverter]:
        converter = Config.converters.get(annotation)

        if converter is None:
            raise ArcError(
                f"'{annotation}' not a valid converter.",
                "If this is a custom converter make sure it is in Config.converters",
            )

        return converter
