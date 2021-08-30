"""
.. include:: ../README.md
"""
from typing import Annotated
from arc import callbacks
from arc.cli import CLI, run
from arc.command import Context, command, namespace
from arc.types import (
    Meta,
    ParamType,
    WrappedVarPositional as VarPositional,
    WrappedVarKeyword as VarKeyword,
)


from arc.config import config
from arc.errors import ExecutionError, ValidationError
from arc.result import Err, Ok, Result


__version__ = "4.0.0"
