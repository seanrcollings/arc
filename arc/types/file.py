from __future__ import annotations
import abc
import io
import sys
import typing as t

from arc import errors
from arc.types.convert import convert_type
from arc.types.default import Default, unwrap
from arc.types.type_arg import TypeArg
from arc.types.type_info import TypeInfo
from arc.types.aliases import Alias

if t.TYPE_CHECKING:
    from arc import Context

__all__ = ["File", "Stdin", "StdinFile", "Stream"]


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


class File(t.IO[str], abc.ABC):
    """Obtains a handler to a file. Handles
    the access to the file, and gurantees that
    it is closed before exiting.


    ## Example
    ```py
    @arc.command
    def command(file: File.Read):
        arc.print(file.read())
    ```

    There are constants defined on `File` (like `File.Read` above) for
    all common actions (`Read`, `Write`, `Append`, `ReadWrite`, etc...).
    View all of them below.

    If none of the pre-defiend constants match your needs, you can customize
    it with an `Annotated` type.

    ```py
    @arc.command
    def command(file: Annotated[File, File.Args(...)]):
        arc.print(file.read())
    ```

    `File.Args`'s call signature matches that of `open` (minus the filename), so
    all of the same properties apply

    `File` is Abstract and cannot be instantiated on it's own
    """

    class Args(TypeArg):
        __slots__ = (
            "mode",
            "buffering",
            "encoding",
            "errors",
            "newline",
            "closefd",
            "opener",
        )

        def __init__(
            self,
            mode: str = Default("r"),
            buffering: int = Default(-1),
            encoding: t.Optional[str] = Default(None),
            errors: OpenErrors = Default(None),
            newline: OpenNewline = Default(None),
            closefd: bool = Default(True),
            opener: t.Optional[t.Callable[..., t.Any]] = Default(None),
        ):
            self.mode = mode
            self.buffering = buffering
            self.encoding = encoding
            self.errors = errors
            self.newline = newline
            self.closefd = closefd
            self.opener = opener

    Read = t.Annotated[t.TextIO, Args(mode="r")]
    """Equivalent to `open(filename, "r")`"""
    Write = t.Annotated[t.TextIO, Args(mode="w")]
    """Equivalent to `open(filename, "w")`"""
    ReadWrite = t.Annotated[t.TextIO, Args(mode="r+")]
    """Equivalent to `open(filename, "r+")`"""
    CreateWrite = t.Annotated[t.TextIO, Args(mode="x")]
    """Equivalent to `open(filename, "x")`"""
    Append = t.Annotated[t.TextIO, Args(mode="a")]
    """Equivalent to `open(filename, "a")`"""
    AppendRead = t.Annotated[t.TextIO, Args(mode="a+")]
    """Equivalent to `open(filename, "a+")`"""

    BinaryRead = t.Annotated[t.BinaryIO, Args("rb")]
    """Equivalent to `open(filename, "rb")`"""
    BinaryWrite = t.Annotated[t.BinaryIO, Args("wb")]
    """Equivalent to `open(filename, "wb")`"""
    BinaryReadWrite = t.Annotated[t.BinaryIO, Args("rb+")]
    """Equivalent to `open(filename, "rb+")`"""
    BinaryCreateWrite = t.Annotated[t.BinaryIO, Args("xb")]
    """Equivalent to `open(filename, "xb")`"""
    BinaryAppend = t.Annotated[t.BinaryIO, Args("ab")]
    """Equivalent to `open(filename, "ab")`"""
    BinaryAppendRead = t.Annotated[t.BinaryIO, Args("ab+")]
    """Equivalent to `open(filename, "ab+")`"""


class Stream(t.IO[str], abc.ABC):
    name = "stream"

    @classmethod
    def __convert__(cls, value: str, info: TypeInfo[t.Any]) -> "t.IO[str]":
        arg: Stream.Args = TypeArg.ensure(
            t.cast(t.Optional[Stream.Args], info.type_arg), cls.__name__
        )

        if value == unwrap(arg.char):
            return arg.stream

        raise errors.ConversionError(
            value, f"expected {unwrap(arg.char)!r} to read from stdin"
        )

    class Args(TypeArg):
        __slots__ = ("stream", "char")

        def __init__(self, stream: t.IO[str] = sys.stdin, char: str = Default("-")):
            self.stream = stream
            self.char = char


Stdin = t.Union[t.Annotated[Stream, Stream.Args(sys.stdin)], io.StringIO]
"""Read input from command line, or from stdin if `-` is passed as the argument"""


_FileOrStdin = t.Union[File.Read, t.Annotated[Stream, Stream.Args(sys.stdin)]]
_info: TypeInfo[t.Any] = TypeInfo.analyze(_FileOrStdin)


class StdinFile(Stream):
    """Read input from a file, or from a stdin if '-' is passed as the argument"""

    @classmethod
    def __convert__(cls, value: str, info: TypeInfo[t.Any]) -> "t.IO[str]":
        try:
            return convert_type(_info.resolved_type, value, _info)
        except errors.ConversionError as e:
            raise errors.ConversionError(
                value, f"expected file or '-' to read from stdin"
            ) from e
