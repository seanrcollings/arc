from typing import Any
from arc import config
from arc.convert.alias import convert_alias, is_alias
from arc._utils import symbol
from arc.types import needs_cleanup

NO_DEFAULT = symbol("NO_DEFAULT")


class Option:
    def __init__(self, param=None, data_dict=None):
        if param:
            self.name = param.name

            if param.annotation == param.empty:
                self.annotation = str
            else:
                self.annotation = param.annotation

            if is_alias(self.annotation):
                name = self.annotation.__origin__.__name__
            elif isinstance(self.annotation, type):
                name = self.annotation.__name__
            elif isinstance(self.annotation, object):
                name = self.annotation.__class__.__name__

            self.converter = config.get_converter(name)

            if param.default == param.empty:
                self.default = NO_DEFAULT
            else:
                self.default = param.default

            self.value = self.default

        elif data_dict:
            self.name, self.annotation, self.default = data_dict
            self.converter = config.get_converter(str)

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
        if is_alias(self.annotation):
            self.value = convert_alias(self.annotation, self.value)
        else:
            self.value = self.converter(self.annotation).convert_wrapper(self.value)

    def cleanup(self):
        if needs_cleanup(self.annotation):
            # Any special types need to implement
            # the __del__ magic method to preform cleanup
            del self.value
