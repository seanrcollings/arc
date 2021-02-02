import logging
from typing import Type, Any, List, Union, Optional
from pathlib import Path


from arc.convert.converters import *
from arc.convert import BaseConverter, converter_mapping, get_converter
from arc.errors import ArcError, ConversionError


class Config:
    """Arc Config object. Singleton object, when attempting
    to instance a new object, if _instace already exists, it
    will be returned instead"""

    _instance: Optional["Config"] = None

    # __not_preloadable lists config options that cannot be loaded
    # in an .arc file. These usually include things that require objects or
    # classes to be loaded with them, like converters. Could potentially
    # allow things like that to be loaded dynamically but that sound annoying
    # so probably not.
    __not_preloadable = ["converters"]

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance

        obj = super().__new__(cls)
        cls._instance = obj
        return obj

    def __init__(self):
        self._loaded = False

        # Set defaults
        self.utility_seperator: str = ":"
        self.options_seperator: str = "="
        self.flag_denoter: str = "--"
        self.loglevel: int = logging.WARNING
        self.anon_identifier: str = "anon"

        self.converters = converter_mapping

        self.__setup_logging()

    @property
    def instance(self) -> Optional["Config"]:
        return self._instance

    def set_value(self, name: str, value: Any):
        if name in self.__dict__:
            # Check that the types match
            current_type = type(getattr(self, name))
            if not isinstance(value, current_type):
                raise ArcError(
                    (
                        f"Config {name} must be set to type:"
                        f"'{current_type}'"
                        f"\nProvided type: {type(value)}"
                    )
                )

        setattr(self, name, value)
        self.__setup_logging()

    def __setup_logging(self):
        logger = logging.getLogger("arc_logger")
        levels = (
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        )

        if self.loglevel not in levels:
            raise ValueError(f"`{self.loglevel}` not a valid logging level")

        logger.setLevel(self.loglevel)

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
        if arcfile.startswith("~"):
            config_file = (Path.home() / arcfile[2:]).resolve()
        else:
            config_file = Path(arcfile).resolve()

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
            StringBoolConverter,
            IntConverter,
            FloatConverter,
            ListConverter,
        ]

        for converter in config_converters:
            try:
                value = converter(converter.convert_to).convert(value)
                break
            except ConversionError:
                continue

        self.set_value(name, value)
