from typing import Type, Union, _GenericAlias
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
            if isinstance(param.annotation, _GenericAlias):
                raise ArcError(
                    "Arc currently does not suppot type aliases :(",
                    "\n In the future, I would like to add support for them",
                    "(https://github.com/seanrcollings/arc/issues/13 )",
                )
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
        """Converts self.value using the converter found by get_converter"""
        # Consider removing the converter_wrapper and simply catching the error in here?
        self.value = self.converter().convert_wrapper(self.value)

    @staticmethod
    def get_converter(annotation: str) -> Type[BaseConverter]:
        """Finds the converter Class for the specified annotation

        :raises ArcError: If no converter is found
        :returns converter: Type[BaseConverter]
        """
        converter: Union[Type[BaseConverter], None] = Config.converters.get(annotation)

        if converter is None:
            raise ArcError(
                f"'{annotation}' not a valid converter.",
                "If this is a custom converter make sure it is in Config.converters",
            )

        return converter
