from __future__ import annotations
import typing as t
import builtins
import sys

from arc.color import colorize, fg
from arc.present.ansi import Ansi
from arc.present.joiner import Join

if t.TYPE_CHECKING:
    from arc.define.command import Command


def print(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    file: t.IO | None = None,
    flush: bool = False,
):
    """A wrapper around `print()` that handles removing escape
    codes when the output is not a TTY"""
    file = file or sys.stdout

    if file and not file.isatty():
        values = tuple(Ansi.clean(str(v)) for v in values)

    builtins.print(*values, sep=sep, end=end, file=file, flush=flush)


def err(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    flush: bool = False,
):
    """Wrapper around `print()` that emits to `stderr` instead of `stdout`"""
    print(*values, sep=sep, end=end, file=sys.stderr, flush=flush)


def info(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    flush: bool = False,
):
    """Wrapper around `print()` that emits to `stderr` instead of `stdout`"""
    print(*values, sep=sep, end=end, file=sys.stderr, flush=flush)


def usage(command: Command):
    """Display the usage string for a given command object. Writes it to `stderr`"""
    info(command.doc.usage())
