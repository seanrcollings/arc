from arc.config import arc_config

from arc.cli import CLI, run
from arc.command import Context, namespace, callbacks
from arc.errors import NoOpError, ExecutionError

NO_OP = NoOpError()

__version__ = "2.4.0"
