class ArcType:
    """Class that each Type sublcasses
    to provide a signal to the converter process"""


# pylint: disable=wrong-import-position
from .file import File
from .range import Range
from .paths import *


def needs_cleanup(kind):
    return kind in (File,)
