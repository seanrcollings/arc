from cli.converter import *


class Config:
    converters = {
        "str": StringConverter,
        "int": IntConverter,
        "float": FloatConverter,
        "byte": ByteConverter,
        "bool": BoolConverter,
        "sbool": StringBoolConverter,
        "ibool": IntBoolConverter
    }
