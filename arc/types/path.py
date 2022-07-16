import pathlib
import typing as t

from arc import errors
from arc.autocompletions import Completion, CompletionInfo, CompletionType


__all__ = ["ValidPath", "FilePath", "DirectoryPath"]

# The concrete implementation of Path isn't chosen
# until instantiation, so you can't sublcass Path directly.
# We can get around this by getting the type of an instance
# of Path
PathType = type(pathlib.Path())


class ValidPath(PathType):  # type: ignore
    valid: t.ClassVar[bool] = True
    directory: t.ClassVar[bool] = False
    file: t.ClassVar[bool] = False

    def __new__(cls, value: str):
        return cls.validate(value)

    @classmethod
    def validate(cls, value: str) -> pathlib.Path:
        path = pathlib.Path(value)

        if cls.valid and not path.exists():
            raise ValueError(f"{value} is not a file or directory")

        if cls.directory and not path.is_dir():
            raise ValueError(f"{value} is a file, not a directory")

        if cls.file and not path.is_file():
            raise ValueError(f"{value} is a directory, not a file")

        return path

    @classmethod
    def __convert__(cls, value: str):
        try:
            return cls(value)
        except ValueError as e:
            raise errors.ConversionError(value, str(e)) from e

    @classmethod
    def __completions__(cls, info: CompletionInfo, _param):
        res = []
        if cls.directory:
            res.append(Completion(info.current, CompletionType.DIR))
        if cls.file or len(res) == 0:
            res.append(Completion(info.current, CompletionType.FILE))

        return res


class FilePath(ValidPath):
    file = True


class DirectoryPath(ValidPath):
    directory = True
