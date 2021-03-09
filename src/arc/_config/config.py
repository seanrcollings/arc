from typing import Type, Union

from arc.convert.converters import *
from arc.convert import BaseConverter, get_converter
from arc.errors import ArcError

from .helpers import *
from .base import ConfigBase


class Config(ConfigBase):
    namespace_sep: ConfigValue[str] = ConfigValue()
    arg_assignment: ConfigValue[str] = ConfigValue()
    flag_denoter: ConfigValue[str] = ConfigValue()
    loglevel: ManagedLogging = ManagedLogging("arc_logger")
    converters: ConfigValue[Dict[str, Type[BaseConverter]]] = ConfigValue()

    # Converter Methods
    def add_converter(self, cls: Type[BaseConverter]):
        """Adds a converter to self.converters
        :param cls: The Custom converter to be added. Must inherit from BaseConverter

        :raises ArcError: if cls is not a sublcass of BaseConverter
        """

        if issubclass(cls, BaseConverter):
            self.converters[cls.convert_to.__name__] = cls
        else:
            raise ArcError("Converter must inherit from 'Base Converter'")

    def get_converter(self, key: Union[str, type]):
        return get_converter(key)
