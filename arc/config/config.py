from typing import Type, Dict

from arc.convert.converters import *
from arc.convert.converters import BaseConverter
from arc.convert import get_converter, converter_mapping
from arc.errors import ArcError

from .helpers import *
from .base import ConfigBase


class Config(ConfigBase):
    namespace_sep: str = ":"
    arg_assignment: str = "="
    flag_denoter: str = "--"
    mode: str = "debug"
    loglevel: ManagedLogging = ManagedLogging("arc_logger")
    converters: Dict[type, Type[BaseConverter]] = converter_mapping

    # Converter Methods
    def add_converter(self, cls: Type[BaseConverter], to: type):
        """Adds a converter to self.converters
        :param cls: The Custom converter to be added. Must inherit from BaseConverter

        :raises ArcError: if cls is not a sublcass of BaseConverter
        """

        if issubclass(cls, BaseConverter):
            self.converters[to] = cls
        else:
            raise ArcError("Converter must inherit from 'Base Converter'")

    def get_converter(self, key: type):
        return get_converter(key)
