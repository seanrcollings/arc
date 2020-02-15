import re
import sys

def parse_options(options):
    parsed = []
    valid_converters = {
        "int": int,
        "float": float,
        "byte": str.encode,
        "bool": str_to_bool
    }
    if options is not None:
        for option in options:
            option_dict = {"name": option, "converter": str}
            match = re.search("<.*:.*>", option)
            if match is not None:
                converter, name = option.lstrip("<").rstrip(">").split(":")
                if converter in valid_converters:
                    option_dict["name"], option_dict["converter"] = name, valid_converters[converter]
                else:
                    print(f"'{converter}' is not a valid conversion identifier")
            parsed.append(option_dict)

    return parsed

def str_to_bool(value):
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    else:
        print(f"Error: string {value} coult not be converted to a boolean")
        sys.exit(1)