import abc
import typing as t


class File(t.IO, abc.ABC):
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
    Write = t.Annotated[t.TextIO, "w"]
    ReadWrite = t.Annotated[t.TextIO, "r+"]
    CreateWrite = t.Annotated[t.TextIO, "x"]
    Append = t.Annotated[t.TextIO, "a"]
    AppendRead = t.Annotated[t.TextIO, "a+"]

    BinaryRead = t.Annotated[t.BinaryIO, "rb"]
    BinaryWrite = t.Annotated[t.BinaryIO, "wb"]
    BinaryReadWrite = t.Annotated[t.BinaryIO, "r+b"]
    BinaryCreateWrite = t.Annotated[t.BinaryIO, "xb"]
    BinaryAppend = t.Annotated[t.BinaryIO, "ab"]
    BinaryAppendRead = t.Annotated[t.BinaryIO, "a+b"]
