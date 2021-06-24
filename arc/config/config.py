from arc.convert.converters import *
from arc.convert.converters import BaseConverter

from .helpers import *
from .base import ConfigBase


class Config(ConfigBase):
    namespace_sep: str = ":"
    arg_assignment: str = "="
    flag_denoter: str = "--"
    mode: str = "debug"
    loglevel: ManagedLogging = ManagedLogging("arc_logger")
