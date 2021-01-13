from typing import Any
from arc import config
from arc.convert import is_alias
from arc._utils import symbol
from arc.types import needs_cleanup, ArcGeneric

NO_DEFAULT = symbol("NO_DEFAULT")


class Option:
    def __init__(self, param=None, data_dict=None):
        if param:
            self.name = param.name

            self.annotation = (
                Any if param.annotation == param.empty else param.annotation
            )

            self.default = NO_DEFAULT if param.default == param.empty else param.default
            self.value = self.default

        elif data_dict:
            self.name = data_dict["name"]
            self.annotation = data_dict["annotation"]
            self.default = data_dict["default"]
            self.value = self.default

        else:
            raise ValueError(
                "Option class must be provided a Parameter"
                + "object or a dictionary containing the information"
            )

    def __repr__(self):
        return f"<Option : {self.name}>"

    def convert(self):
        """Converts self.value using the converter found by get_converter"""
        if self.annotation is Any:
            return

        name = self.get_converter_name()
        converter = config.get_converter(name)

        self.value = converter(self.annotation).convert_wrapper(self.value)

    def get_converter_name(self) -> str:
        """Returns the converter name for
        the option's annotation
        """

        if is_alias(self.annotation):
            if issubclass(self.annotation.__origin__, ArcGeneric):  # type: ignore
                return self.annotation.__origin__.__name__.lower()  # type: ignore
            else:
                return "alias"
        return self.annotation.__name__

    def cleanup(self):
        # Any special types need to implement
        # the __del__ magic method to preform cleanup
        if needs_cleanup(self.annotation):
            del self.value
