from __future__ import annotations

import builtins
import datetime
import sys
import typing as t
from contextlib import contextmanager

from arc.present.ansi import Ansi, colorize, fg, fx

if t.TYPE_CHECKING:
    from arc.runtime import Context

T = t.TypeVar("T", bytes, str)


class Console:
    def __init__(
        self,
        default_print_stream: t.IO[str] | None = None,
        default_log_stream: t.IO[str] | None = None,
        show_icons: bool = True,
        color_output: bool = True,
        indent: str = "  ",
    ) -> None:
        self.default_print_stream = default_print_stream or sys.stdout
        self.default_log_stream = default_log_stream or sys.stderr
        self.show_icons = show_icons
        self.color_output = color_output
        self._indent = indent
        self._indent_count = 0
        self.icons: dict[str, str] = {
            "ok": "✓",
            "error": "✗",
            "act": "",
            "warn": "🚧",
            "subtle": "",
            "snake": "🐍",
        }

    def print(
        self,
        *values: object,
        sep: str | None = None,
        end: str | None = None,
        file: t.IO[str] | None = None,
        flush: bool = False,
    ) -> None:
        """A wrapper around `print()` that handles removing escape
        codes when the output is not a TTY"""
        file = file or self.default_print_stream

        if (file and not file.isatty()) or not self.color_output:
            values = tuple(Ansi.clean(str(v)) for v in values)

        if self._indent_count and values:
            first, *rest = values
            first = f"{self._indent * self._indent_count}{first}"
            values = (first, *rest)

        builtins.print(*values, sep=sep, end=end, file=file, flush=flush)

    def info(
        self,
        *values: object,
        sep: str | None = None,
        end: str | None = None,
        flush: bool = False,
    ) -> None:
        """Wrapper around `print()` that emits to the
        `Console.log` stream instead of the `Console.print` stream"""
        self.print(*values, sep=sep, end=end, file=self.default_log_stream, flush=flush)

    def log(
        self,
        /,
        first: object = None,
        *values: object,
        sep: str | None = None,
        end: str | None = None,
        file: t.IO[str] | None = None,
        flush: bool = False,
    ) -> None:
        """Useful for simple logging. Writes to stderr
        instead of stdout and includes a timestamps"""
        file = file or self.default_log_stream
        time = datetime.datetime.now().strftime("%H:%M:%S")
        first = first or ""
        first = colorize(f"[{time}] ", fg.GREY) + str(first)
        self.print(first, *values, sep=sep, end=end, file=file, flush=flush)

    @contextmanager
    def indent(self) -> t.Generator[None, None, None]:
        """Context manager that will indent
        any prints done within it's block"""
        try:
            self._indent_count += 1
            yield
        finally:
            self._indent_count -= 1

    def _decorate(
        self,
        *values: object,
        color: str = "",
        icon: str = "",
        **kwargs: t.Any,
    ) -> None:
        if len(values) == 0:
            self.print(**kwargs)
            return

        first = values[0]
        rest = values[1:-1]
        last = values[-1]

        if self.show_icons and icon:
            first = f"{icon} {first}"

        if self.color_output and color:
            if len(values) > 1:
                first = f"{color}{first}"
                last = f"{last}{fx.CLEAR}"
            else:
                first = f"{color}{first}{fx.CLEAR}"

        objects = [first, *rest]
        if len(values) > 1:
            objects.append(last)

        self.print(
            *objects,
            **kwargs,
        )

    def rule(self, string: str = "", width: int = 80, **kwargs: t.Any) -> None:
        """Display a horizontal rule to the user"""
        self.print(string.center(width, "─"), **kwargs)

    def ok(self, *values: object, **kwargs: t.Any) -> None:
        """Display a successful message to the user"""
        self._decorate(*values, color=fg.GREEN, icon=self.icons["ok"], **kwargs)

    def err(self, *values: object, **kwargs: t.Any) -> None:
        """Display an unsuccessful message to the user"""
        self._decorate(*values, color=fg.RED, icon=self.icons["error"], **kwargs)

    def act(self, *values: object, **kwargs: t.Any) -> None:
        """Display an action message to the user"""
        self._decorate(*values, color=fg.BLUE, icon=self.icons["act"], **kwargs)

    def warn(self, *values: object, **kwargs: t.Any) -> None:
        """Display a warning message to the user"""
        self._decorate(*values, color=fg.YELLOW, icon=self.icons["warn"], **kwargs)

    def subtle(self, *values: object, **kwargs: t.Any) -> None:
        """Display a subtle (light grey) message to the user"""
        self._decorate(*values, color=fg.GREY, icon=self.icons["subtle"], **kwargs)

    def snake(self, *values: object, **kwargs: t.Any) -> None:
        """Display a Pythonic message to the user"""
        self._decorate(*values, icon=self.icons["snake"], **kwargs)

    @classmethod
    def __depends__(cls, ctx: Context) -> Console:
        return cls()
