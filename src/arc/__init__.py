from arc._config import Config

config = Config()

# # pylint: disable=wrong-import-position
from arc.cli import CLI, run
from arc.command import CommandType, namespace
from arc.errors import NoOpError

NO_OP = NoOpError()

__version__ = "1.0.1"
