"""Global Variables bad- >:( Global variables wrapped in a class :)
In reality, these configs should only be set in the setup of the CLI, not after
They are also not changed by the program as it executes.
They will also be loaded from a .arc file
"""
import os
from typing import Type, Dict, Any, List
from arc.convert.converters import *
from arc.convert import BaseConverter
from arc.errors import ArcError, ConversionError


class Config:
    # __not_preloadable lists config options that cannot be loaded
    # in an .arc file. These usually include things that require objects or
    # classes to be loaded with them, like converters
    __not_preloadable = "converters"
    _loaded = False

    # Set defaults
    utility_seperator: str = ":"
    options_seperator: str = "="
    flag_denoter: str = "--"
    log: bool = False
    debug: bool = False
    decorate_text: bool = True
    anon_identifier: str = "anon"

    converters: Dict[str, Type[BaseConverter]] = {
        "str": StringConverter,
        "int": IntConverter,
        "float": FloatConverter,
        "bytes": BytesConverter,
        "bool": BoolConverter,
        "sbool": StringBoolConverter,
        "ibool": IntBoolConverter,
        "list": ListConverter,
    }

    @classmethod
    def set_value(cls, name: str, value: Any):
        if name in cls.__dict__:
            # Check that the types match
            current_type = type(getattr(cls, name))
            if not isinstance(value, current_type):
                raise ArcError(
                    (
                        f"Config {name} must be set to type:"
                        f"'{current_type}'"
                        f"\nProvided type: {type(value)}"
                    )
                )

        setattr(cls, name, value)

    @classmethod
    def __set_loaded_value(cls, name: str, value: str):
        """Private method, sets a value on the Config class, passed from load_arc_file
        If it already exists on the class, the new value must match the current type,
        if it doesn't exist it's just added on
        """

        if name in Config.__not_preloadable:
            raise ArcError(
                f"'{name}' cannot be configured via the .arc file. "
                + "If you want to configure this, do so within the Python file"
            )

        # Check if it needs to be converted
        config_converters: List[Type[BaseConverter]] = [
            StringBoolConverter,
            ListConverter,
            IntConverter,
            FloatConverter,
        ]

        for converter in config_converters:
            try:
                value = converter().convert(value)
                break
            except ConversionError:
                continue

        cls.set_value(name, value)

    @classmethod
    def load_arc_file(cls, arcfile):
        """Reads in a arc config file and parses it's contents"""
        if not os.path.isfile(arcfile):
            return
            # raise FileNotFoundError(f"arc configuration file '{arcfile}' not found")

        file = open(arcfile)
        lines = file.readlines()
        file.close()
        for line in lines:
            config = line.partition("#")[0].strip("\n")
            if config not in ("", " "):
                if "=" not in config:
                    raise ValueError(
                        "Keys and values must be seperated" + " by '=' in the .arc file"
                    )
                name, value = config.strip().split("=")
                cls.__set_loaded_value(name, value)

        cls._loaded = True

    @classmethod
    def add_converter(cls, obj: Type[BaseConverter]):
        """Adds a converter to self.converters
        :param obj: The Custom converter to be added. Must inherit from BaseConverter

        :raises ArcError: if obj is not a sublcass of BaseConverter
        """
        if issubclass(obj, BaseConverter):
            cls.converters[obj.convert_to.__name__] = obj
        else:
            raise ArcError("Converter must inherit from 'Base Converter'")

    @classmethod
    def get_converter(cls, key):
        return cls.converters.get(key)
