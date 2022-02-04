import pathlib
import typing as t

from arc import errors
from arc.autocompletions import Completion, CompletionInfo, CompletionType
from arc.types import helpers


__all__ = ["ValidPath", "FilePath", "DirectoryPath", "strictpath"]

# The concrete implementation of Path isn't chosen
# until instantiation, so you can't sublcass Path directly.
# We can get around this by getting the type of an instance
# of Path
PathType = type(pathlib.Path())


class ValidPath(PathType):  # type: ignore
    name = "path"
    valid: t.ClassVar[bool] = True
    directory: t.ClassVar[bool] = False
    file: t.ClassVar[bool] = False
    matches: t.ClassVar[t.Optional[str]] = None

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.__validate()

    def __validate(self):
        if self.valid and not self.exists():
            raise ValueError(f"{self} does not exist")

        if self.directory and not self.is_dir():
            raise ValueError(f"{self} is a file, not a directory")

        if self.file and not self.is_file():
            raise ValueError(f"{self} is a directory, not a file")

        if self.matches:
            if (err := helpers.match(self.matches, str(self.resolve()))).err:
                raise ValueError(str(err))

    def resolve(self, strict=False):
        # HACK resolve() creates a new Path object, so
        # __validate will get called recursively when
        # matches is set.
        cls = type(self)
        matches, cls.matches = cls.matches, None
        resolved = super().resolve(strict)
        cls.matches = matches
        return resolved

    @classmethod
    def __convert__(cls, value: str):
        try:
            return cls(value)
        except (AssertionError, ValueError) as e:
            raise errors.ConversionError(value, str(e)) from e

    @classmethod
    def __completions__(cls, info: CompletionInfo):
        res = []
        if cls.file:
            res.append(Completion(info.current, CompletionType.FILE))
        if cls.directory:
            res.append(Completion(info.current, CompletionType.DIR))

        if len(res) == 0:
            res.append(Completion(info.current, CompletionType.FILE))

        return res


class FilePath(ValidPath):
    file = True


class DirectoryPath(ValidPath):
    directory = True


def strictpath(
    valid: bool = True,
    directory: bool = False,
    file: bool = False,
    matches: t.Optional[str] = None,
) -> type[ValidPath]:
    """Creates a custom `ValidPath` type with specific validations

    Args:
        valid (bool, optional): Is a valid path to validate. Defaults to True.
        directory (bool, optional): Path is a directory. Defaults to False.
        file (bool, optional): Path is a file. Defaults to False.
        matches (t.Optional[str], optional): Path matches the given regex.
        Matches to the resolved path. Defaults to None.

    Raises:
        ValueError: If directory and file are both true

    Returns:
        type[ValidPath]: The `StrictPath` type
    """
    if all([directory, file]):
        raise ValueError(
            "directory and file are mutually exclusive and cannot both be true"
        )

    return type(
        "StrictPath",
        (ValidPath,),
        {
            "valid": valid,
            "directory": directory,
            "file": file,
            "matches": matches,
        },
    )
