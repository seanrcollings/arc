"""
.. include:: ../README.md
"""
from arc import callbacks
from arc.cli import CLI, run
from arc.command import command, namespace
from arc.config import config
from arc.errors import ExecutionError, ValidationError
from arc.result import Err, Ok, Result


__version__ = "5.0.0"
