"""
.. include:: ../README.md
"""
from typing import Annotated
from arc import callbacks
from arc.cli import CLI, run
from arc.command import Context, command, namespace
from arc.types.params import (
    Meta,
    meta,
    ParamType,
    VarPositional,
    VarKeyword,
)

from arc.config import config
from arc.errors import ExecutionError, ValidationError
from arc.result import Err, Ok, Result


__version__ = "5.0.0"       