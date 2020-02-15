import re
import sys
from app.converter import *

def parse_options(options):
    '''
        Parses provided options, checking for a converter
        :param options - array of strings. Can have a converter
            associated with it.
            - without converter "normal_string"
            - with converter "<int:number>
        :return - a new array of dictionaries of the parsed options
            each option looks like this:
                {
                    "name": "number"
                    "converter": IntConverter
                }
            if no converter was specified, StringConverter is used

    '''
    parsed = []
    valid_converters = {
        "int": IntConverter,
        "float": FloatConverter,
        "byte": ByteConverter,
        "bool": BoolConverter
    }

    if options is not None:
        for option in options:
            option_dict = {"name": option, "converter": StringConverter}
            match = re.search("<.*:.*>", option) # Matches to "<convertername:varname>""
            if match is not None:
                converter, name = option.lstrip("<").rstrip(">").split(
                    ":")  # turns "<convertername:varname>" into ["convertername", "varname"]
                if converter in valid_converters:
                    option_dict["name"], option_dict["converter"] = name, valid_converters[converter]
                else:
                    print(f"'{converter}' is not a valid conversion identifier")
            parsed.append(option_dict)

    return parsed
