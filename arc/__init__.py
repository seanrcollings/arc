"""
.. include:: ../README.md
"""
from arc.cli import CLI
from arc._command import Command
from arc.command_builders import command, namespace
from arc.config import config
from arc.errors import ExecutionError, ValidationError, ConversionError
from arc.result import Err, Ok, Result
from arc.context import Context
from arc.types import *
from arc.params import Param, Option, Flag, Argument, Count

__version__ = "6.3.0b3"
