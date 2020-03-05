from arc.config import Config
from arc.errors import ArcError
from arc.converter import *
from arc.converter import is_converter


class Option:
    def __init__(self, option):
        self.name, self.converter = self.parse(option)

    def __repr__(self):
        return f"<Option : {self.name}>"

    def __call__(self, value):
        return self.name, self.converter(value)

    @staticmethod
    def parse(option: str) -> str:  # One of the converters
        '''Parses provided option into name and converter

        Checks for a type converter
        :param options - array of strings. Can have a converter
            associated with it.
            - without converter "normal_string"
            - with converter "<int:number>"
        :returns: name of option, converter class
            StringConverter is default converter
        '''
        name = option
        converter = StringConverter

        if option.startswith("<") and option.endswith(">"):
            if not is_converter(option):
                raise ArcError(f"'{option}' does not conform",
                               "to converter syntax")

            # turns "<convertername:varname>" into ["convertername", "varname"]
            converter, name = option.lstrip("<").rstrip(">").split(":")

            if converter not in Config.converters:
                raise ArcError(f"'{converter}' is not a valid",
                               "conversion identifier")

            converter = Config.converters[converter]

        return name, converter
