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

__version__ = "6.2.2"
