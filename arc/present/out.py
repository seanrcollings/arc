from __future__ import annotations

import typing as t

from arc.present.console import Console

if t.TYPE_CHECKING:
    from arc.define.command import Command

_console: Console | None = None


def _default_console() -> Console:
    global _console
    if not _console:
        _console = Console()
    return _console


def print(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    file: t.IO[str] | None = None,
    flush: bool = False,
) -> None:
    """A wrapper around `print()` that handles removing escape
    codes when the output is not a TTY"""

    _default_console().print(*values, sep=sep, end=end, file=file, flush=flush)


def info(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    flush: bool = False,
) -> None:
    """Wrapper around `print()` that emits to `stderr` instead of `stdout`"""
    _default_console().info(*values, sep=sep, end=end, flush=flush)


def log(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    file: t.IO[str] | None = None,
    flush: bool = False,
) -> None:
    """`print()` to stderr with a timestamp"""
    _default_console().log(*values, sep=sep, end=end, file=file, flush=flush)


def err(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    flush: bool = False,
) -> None:
    """Wrapper around `print()` that emits to an error in red"""
    _default_console().err(*values, sep=sep, end=end, flush=flush)


def usage(command: Command) -> None:
    """Display the usage string for a given command object. Writes it to `stderr`"""
    info(command.doc.usage())
