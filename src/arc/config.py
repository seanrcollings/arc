from arc.converter import *


class Config:
    converters = {
        "str": StringConverter,
        "int": IntConverter,
        "float": FloatConverter,
        "byte": ByteConverter,
        "bool": BoolConverter,
        "sbool": StringBoolConverter,
        "ibool": IntBoolConverter,
        "list": ListConverter
    }
    seperator = "="
    logger_level = 20
