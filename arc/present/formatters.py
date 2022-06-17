# https://github.com/pallets/click/blob/main/src/click/formatting.py
import shutil
from contextlib import contextmanager
import textwrap
import typing as t

from arc.utils import ansi_len

DEFAULT_MAX_WIDTH = 80


class TextFormatter:
    def __init__(
        self,
        indent_increment: int = 4,
        width: int = None,
        max_width: int = DEFAULT_MAX_WIDTH,
    ):
        self.indent_increment = indent_increment

        if width is None:
            width = max_width
            width = min(shutil.get_terminal_size().columns, width) - 2

        self.width = width
        self.current_indent = 0
        self._buffer: list[str] = []

    @property
    def value(self):
        """Current value of the formatter"""
        return "".join(self._buffer)

    def indent(self):
        """Indents text by `indent_increment`"""
        self.current_indent += self.indent_increment

    def dedent(self):
        """Dedents text by `indent_increment`"""
        self.current_indent -= self.indent_increment

    def write(self, string: str):
        self._buffer.append(string)

    def write_heading(self, heading: str):
        self.write(f"{'':>{self.current_indent}}{heading}\n")

    def write_text(self, text: t.Union[str, list[str]]):
        self.write(
            self.wrap_text(
                text,
                width=self.width,
                initial_indent=" " * self.current_indent,
                subsequent_indent=" " * self.current_indent,
            )
        )

    def write_paragraph(self):
        if self._buffer:
            self.write("\n")

    # TODO: This is not handling colored text properly :(
    def wrap_text(
        self,
        text: t.Union[str, list[str]],
        width: int,
        initial_indent: str = "",
        subsequent_indent: str = "",
        paragraph_seperator: str = "\n\n",
    ):
        if isinstance(text, str):
            text = [text]

        wrapped = ""

        wrapper = textwrap.TextWrapper(
            width=width,
            initial_indent=initial_indent,
            subsequent_indent=subsequent_indent,
            replace_whitespace=True,
            drop_whitespace=True,
        )

        for para in text:
            if para.startswith("\b"):
                wrapped += (
                    self.wrap_text(
                        para.lstrip("\b\n").split("\n"),
                        width,
                        initial_indent,
                        subsequent_indent,
                        "\n",
                    )
                    + paragraph_seperator
                )
            else:
                width = width + (len(para) - ansi_len(para))
                wrapper.width = width
                wrapped += wrapper.fill(para) + paragraph_seperator

        return wrapped.rstrip("\n")

    @contextmanager
    def indentation(self):
        self.indent()
        try:
            yield
        finally:
            self.dedent()

    @contextmanager
    def section(self, name: str):
        self.write_paragraph()
        self.write_heading(name)
        self.indent()

        try:
            yield
        finally:
            self.dedent()
            self.write_paragraph()
