import abc
import typing as t


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
    def command(file: Annotated[File, File.Meta(...)]):
        print(file.read())
    ```

    `File.Meta`'s call signature matches that of `open` (minus the filename), so
    all of the same properties apply

    `File` is Abstract and cannot be instantiated on it's own
    """

    @staticmethod
    def Meta(
        mode: str = "r",
        buffering: int = -1,
        encoding: str = None,
        errors=None,
        newline: str = None,
        closefd: bool = True,
        opener=None,
    ):
        return {
            "mode": mode,
            "buffering": buffering,
            "encoding": encoding,
            "errors": errors,
            "newline": newline,
            "closefd": closefd,
            "opener": opener,
        }

    Read = t.Annotated[t.TextIO, "r"]
    """Equivelant to `open(filename, "r")"""
    Write = t.Annotated[t.TextIO, "w"]
    """Equivelant to `open(filename, "w")"""
    ReadWrite = t.Annotated[t.TextIO, "r+"]
    """Equivelant to `open(filename, "r+")"""
    CreateWrite = t.Annotated[t.TextIO, "x"]
    """Equivelant to `open(filename, "x")"""
    Append = t.Annotated[t.TextIO, "a"]
    """Equivelant to `open(filename, "a")"""
    AppendRead = t.Annotated[t.TextIO, "a+"]
    """Equivelant to `open(filename, "a+")"""

    BinaryRead = t.Annotated[t.BinaryIO, "rb"]
    """Equivelant to `open(filename, "rb")"""
    BinaryWrite = t.Annotated[t.BinaryIO, "wb"]
    """Equivelant to `open(filename, "wb")"""
    BinaryReadWrite = t.Annotated[t.BinaryIO, "r+b"]
    """Equivelant to `open(filename, "r+b")"""
    BinaryCreateWrite = t.Annotated[t.BinaryIO, "xb"]
    """Equivelant to `open(filename, "xb")"""
    BinaryAppend = t.Annotated[t.BinaryIO, "ab"]
    """Equivelant to `open(filename, "ab")"""
    BinaryAppendRead = t.Annotated[t.BinaryIO, "a+b"]
    """Equivelant to `open(filename, "a+b")"""
