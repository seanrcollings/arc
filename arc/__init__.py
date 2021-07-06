"""
.. include:: ../README.md
"""
from arc.config import config
from arc.cli import CLI, run
from arc.command import Context, namespace, ParsingMethod
from arc import callbacks
from arc.errors import NoOpError, ExecutionError, ValidationError

NO_OP = NoOpError()

__version__ = "3.1.0    "
