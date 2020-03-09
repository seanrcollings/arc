'''Global Variables bad- >:( Global variables wrapped in a class :)
In reality, these configs should only be set in the setup of the CLI, not after
They are also not changed by the program as it executes.
They will also be _loaded from a .arc file
'''
import os
from arc.converter import *
from arc.errors import ArcError


class Config:
    utility_seperator = ":"
    options_seperator = "="
    flag_denoter = "--"
    log = False
    debug = False
    decorate_text = True
    logger_level = 1

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

    # __not_preloadable lists config options that cannot be _loaded
    # in an .arc file. These usually include things that require objects or
    # classes to be _loaded with them, like converters
    __not_preloadable = ('converters')

    _loaded = False

    @classmethod
    def set_value(cls, name: str, value: str):
        '''Sets a value on the Config class, passed from load_arc_file

        The name must already be a value on the Config class, and the value
        must match the already set value
        '''
        # Check that it can be changed
        if name not in cls.__dict__:
            raise ArcError(f"'{name}' is not an acceptable configuration name")
        if name in cls.__not_preloadable:
            raise ArcError(
                f"'{name}' cannot be configured via the .arc file. " +
                "If you want to configure this, do so within the Python file")

        # Check if it needs to be converted
        if value.isnumeric():
            value = int(value)
        elif value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False

        # Check that the types match
        current_type = type(getattr(Config, name))
        if isinstance(value, current_type):
            setattr(Config, name, value)
        else:
            raise ArcError((f"Config {name} must be set to type:"
                            f"'{current_type}'"
                            f"\nProvided type: {type(value)}"))

    @classmethod
    def load_arc_file(cls, arcfile):
        if os.path.isfile(arcfile):
            file = open(arcfile)
            for line in file:
                line = line.partition("#")
                config = line[0]
                if config not in ("", " "):
                    if "=" not in config:
                        raise ValueError("Keys and values must be seperated" +
                                         " by '=' in the .arc file")
                    name, value = config.strip().split("=")
                    cls.set_value(name, value)
            file.close()

        cls._loaded = True
