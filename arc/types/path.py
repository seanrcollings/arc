import pathlib
import typing as t

from arc import errors
from arc.autocompletions import Completion, CompletionInfo, CompletionType

__all__ = ["ValidPath", "FilePath", "DirectoryPath"]


def valid_path(value: pathlib.Path) -> pathlib.Path:
    if not value.exists():
        raise errors.ValidationError(f"{value} is not a file or directory")

    return value


def valid_directory(value: pathlib.Path) -> pathlib.Path:
    if not value.is_dir():
        raise errors.ValidationError(f"{value} is not a directory")

    return value


def valid_file(value: pathlib.Path) -> pathlib.Path:
    if not value.is_file():
        raise errors.ValidationError(f"{value} is not a file")

    return value


ValidPath = t.Annotated[pathlib.Path, valid_path]
FilePath = t.Annotated[pathlib.Path, valid_file]
DirectoryPath = t.Annotated[pathlib.Path, valid_directory]
