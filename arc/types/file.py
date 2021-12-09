import abc
import typing as t
from dataclasses import dataclass
import types
import sys


__all__ = ["File", "Stdin"]

# TODO: What happens with t.Annotated[File.Read, File.Arg(...)]
# Which expands to: t.Annotated[t.TextIO, "r", {...}]
# Options:
# - Ignore the second annotation argument
# - Disallow the second annotation argument
# - Allow it and merge the two


OpenNewline = t.Literal[None, "", "\n", "\r", "\r\n"]
OpenErrors = t.Literal[
    None,
    "strict",
    "ignore",
    "replace",
    "surrogateescape",
    "xmlcharrefreplace",
    "backslashreplace",
    "namereplace",
]


class File(t.IO, abc.ABC):
    """Obtains a handler to a file. Handles
    the access to the file, and gurantees that
    it is closed before exiting.


    ## Example
    ```py
    @cli.command()
    def command(file: File.Read):
        print(file.read())
    ```

    There are constants defined on `File` (like `File.Read` above) for
    all common actions (`Read`, `Write`, `Append`, `ReadWrite`, etc...).
    View all of them below.

    If none of the pre-defiend constants match your needs, you can customize
    it with an `Annotated` type.

    ```py
    @cli.command()
    def command(file: Annotated[File, File.Args(...)]):
        print(file.read())
    ```

    `File.Args`'s call signature matches that of `open` (minus the filename), so
    all of the same properties apply

    `File` is Abstract and cannot be instantiated on it's own
    """

    @dataclass
    class Args:
        mode: str = "r"
        buffering: int = -1
        encoding: t.Optional[str] = None
        errors: OpenErrors = None
        newline: OpenNewline = None
        closefd: bool = True
        opener: t.Optional[t.Callable] = None

    Read = t.Annotated[t.TextIO, "r"]
    """Equivalent to `open(filename, "r")"""
    Write = t.Annotated[t.TextIO, "w"]
    """Equivalent to `open(filename, "w")"""
    ReadWrite = t.Annotated[t.TextIO, "r+"]
    """Equivalent to `open(filename, "r+")"""
    CreateWrite = t.Annotated[t.TextIO, "x"]
    """Equivalent to `open(filename, "x")"""
    Append = t.Annotated[t.TextIO, "a"]
    """Equivalent to `open(filename, "a")"""
    AppendRead = t.Annotated[t.TextIO, "a+"]
    """Equivalent to `open(filename, "a+")"""

    BinaryRead = t.Annotated[t.BinaryIO, "rb"]
    """Equivalent to `open(filename, "rb")"""
    BinaryWrite = t.Annotated[t.BinaryIO, "wb"]
    """Equivalent to `open(filename, "wb")"""
    BinaryReadWrite = t.Annotated[t.BinaryIO, "rb+"]
    """Equivalent to `open(filename, "rb+")"""
    BinaryCreateWrite = t.Annotated[t.BinaryIO, "xb"]
    """Equivalent to `open(filename, "xb")"""
    BinaryAppend = t.Annotated[t.BinaryIO, "ab"]
    """Equivalent to `open(filename, "ab")"""
    BinaryAppendRead = t.Annotated[t.BinaryIO, "ab+"]
    """Equivalent to `open(filename, "ab+")"""


class StandardStream(str):
    _stream: t.ClassVar[t.TextIO]

    @dataclass
    class Args:
        line_breaks: bool = False

    @classmethod
    def __convert__(cls, value, info):
        meta: StandardStream.Args = (  # pylint: disable=used-before-assignment
            info.annotations[0] if len(info.annotations) >= 1 else cls.Args()
        )

        if value == "-":
            if meta.line_breaks:
                return cls._stream.readlines()
            else:
                return cls._stream.read()
        else:
            return cls(value)


class Stdin(StandardStream):
    _stream = sys.stdin
