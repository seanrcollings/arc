from arc._config import Config

config = Config()

# # pylint: disable=wrong-import-position
from arc.cli import CLI, run
from arc.command import CommandType, group

__version__ = "1.0.1"
