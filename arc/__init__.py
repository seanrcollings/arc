"""
.. include:: ../README.md
"""
from arc.cli import CLI
from arc._command import Command
from arc.command_builders import command, namespace
from arc.config import config, configure
from arc.errors import ExecutionError, ValidationError, ConversionError, Exit
from arc.result import Err, Ok, Result
from arc.context import Context
from arc.types import *
from arc.params import Param, Option, Flag, Argument, Count
from arc.error_handlers import create_handler

__version__ = "6.4.0"
