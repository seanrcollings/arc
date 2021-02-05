from arc._config import Config

config = Config()

# pylint: disable=wrong-import-position
from arc.cli import CLI
from arc.utility import Utility
from arc.script import ScriptType

__version__ = "1.2.0"
