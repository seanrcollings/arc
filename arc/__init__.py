"""
.. include:: ../README.md
"""
from arc import callbacks
from arc.cli import CLI, run
from arc.command import (
    Context,
    Meta,
    ParamType,
    VarKeyword,
    VarPositional,
    command,
    namespace,
)
from arc.config import config
from arc.errors import ExecutionError, ValidationError
from arc.result import Err, Ok, Result

__version__ = "4.0.0"
