import logging
from typing import Type, List, Union
from pathlib import Path


from arc.convert.converters import *
from arc.convert import BaseConverter, converter_mapping, get_converter
from arc.errors import ArcError, ConversionError


class ManagedConfigValue:
    def __init__(self):
        self.value = None
        self.type = None
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return self.value

    def __set__(self, obj, value):
        if self.type is None:
            self.type = type(value)

        if not isinstance(value, self.type):
            raise ArcError(
                (
                    f"Config {self.name} must be of type: "
                    f"{self.type}"
                    f"\nProvided type: {type(value)}"
                )
            )
        self.value = value

        self._post_set()

    def _post_set(self):
        """Used to check / process self.value
        should be defined in subclass
        """


class ManagedLogging(ManagedConfigValue):
    def _post_set(self):
        logger = logging.getLogger("arc_logger")
        levels = (
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        )

        if self.value not in levels:
            raise ValueError(f"`{self.value}` not a valid logging level")

        logger.setLevel(self.value)


class Config:
    """Arc Config object. Singleton object, when attempting
    to instance a new object, if _instace already exists, it
    will be returned instead"""

    # __not_preloadable lists config options that cannot be loaded
    # in an .arc file. These usually include things that require objects or
    # classes to be loaded with them, like converters. Could potentially
    # allow things like that to be loaded dynamically but that sound annoying
    # so probably not.
    __not_preloadable = ["converters"]

    namespace_sep = ManagedConfigValue()
    arg_assignment = ManagedConfigValue()
    flag_denoter = ManagedConfigValue()
    loglevel = ManagedLogging()
    converters = ManagedConfigValue()

    def __init__(self):
        self._loaded = False

        # Set defaults
        self.namespace_sep = ":"
        self.arg_assignment = "="
        self.flag_denoter = "--"
        self.loglevel = logging.WARNING
        self.converters = converter_mapping

    # Converter Methods
    def add_converter(self, obj: Type[BaseConverter]):
        """Adds a converter to self.converters
        :param obj: The Custom converter to be added. Must inherit from BaseConverter

        :raises ArcError: if obj is not a sublcass of BaseConverter
        """
        if issubclass(obj, BaseConverter):
            self.converters[obj.convert_to.__name__] = obj
        else:
            raise ArcError("Converter must inherit from 'Base Converter'")

    def get_converter(self, key: Union[str, type]):
        return get_converter(key)

    # Arc file Methods
    def load_arc_file(self, arcfile: str, force=False):
        """Reads in a arc config file and parses it's contents"""
        config_file = Path(arcfile).expanduser().resolve()

        if self._loaded and not force:
            return

        if not config_file.is_file():
            if arcfile == "./.arc":
                return
            raise ArcError(f"File '{arcfile}' does not exist / is not a file")

        file = config_file.open()
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
                self.__set_loaded_value(name, value)

        self._loaded = True

    def __set_loaded_value(self, name: str, value: str):
        """Private method, sets a value on the Config class, passed from load_arc_file
        If it already exists on the class, the new value must match the current type,
        if it doesn't exist it's just added on
        """

        if name in Config.__not_preloadable:
            raise ArcError(
                f"'{name}' cannot be configured via the .arc file. "
                "If you want to configure this, do so within the Python file"
            )

        # Check if it needs to be converted
        config_converters: List[Type[BaseConverter]] = [
            IntConverter,
            BoolConverter,
            FloatConverter,
            ListConverter,
        ]

        for converter in config_converters:
            try:
                value = converter(converter.convert_to).convert(value)
                break
            except ConversionError:
                continue

        setattr(self, name, value)
