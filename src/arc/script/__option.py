from arc.config import Config
from arc.convert.alias import convert_alias, is_alias
from arc._utils import symbol

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
            else:
                name = self.annotation.__name__

            self.converter = Config.get_converter(name)

            if param.default == param.empty:
                self.default = NO_DEFAULT
            else:
                self.default = param.default

            self.value = self.default

        elif data_dict:
            self.name, self.annotation, self.default = data_dict
            self.converter = Config.get_converter("str")

        else:
            raise ValueError(
                "Option class must be provided a Parameter"
                + "object or a dictionary containing the information"
            )

    def __repr__(self):
        return f"<Option : {self.name}>"

    def convert(self):
        """Converts self.value using the converter found by get_converter"""
        if is_alias(self.annotation):
            self.value = convert_alias(self.annotation, self.value)
        else:
            self.value = self.converter().convert_wrapper(self.value)
