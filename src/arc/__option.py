from arc.config import Config
from arc.converter.alias import convert_alias, is_alias


class NoDefault:
    """Type for when a paramater doesn't have a default value"""


class Option:
    def __init__(self, param):
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
            self.default = NoDefault
        else:
            self.default = param.default

        self.value = self.default

    def __repr__(self):
        return f"<Option : {self.name}>"

    def convert(self):
        """Converts self.value using the converter found by get_converter"""
        if is_alias(self.annotation):
            self.value = convert_alias(self.annotation, self.value)
        else:
            self.value = self.converter().convert_wrapper(self.value)
