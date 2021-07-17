"""
.. include:: ../README.md
"""
from arc.config import config
from arc.cli import CLI, run
from arc.command import Context, namespace, ParsingMethod, command
from arc import callbacks
from arc.errors import ExecutionError, ValidationError
from arc.result import Result, Ok, Err


__version__ = "4.0.0"
