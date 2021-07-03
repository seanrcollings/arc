import os
from pathlib import Path, _windows_flavour, _posix_flavour  # type: ignore

from . import ArcType


class ValidPath(Path, ArcType):
    """Custom filepath type that the Conversion
    process will validate before passing to the
    Command function
    """

    _flavour = _windows_flavour if os.name == "nt" else _posix_flavour
