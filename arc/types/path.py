import pathlib
import typing as t
from arc import errors

__all__ = ["ValidPath", "FilePath", "DirectoryPath"]

# The concrete implementation of Path isn't chosen
# until instantiation, so you can't sublcass Path directly
# we can get around this by getting the type of an instance
# of Path
PathType = type(pathlib.Path())


class ValidPath(PathType):  # type: ignore
    _validate = lambda self: self.exists()
    name = "path"

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        if not self._validate():
            self._fail()

    def _fail(self):
        raise ValueError(f"{self} does not exist")

    @classmethod
    def __convert__(cls, value: str):
        try:
            cls(value)
        except AssertionError as e:
            raise errors.ConversionError(value, str(e))


class FilePath(ValidPath):
    _validate = lambda self: self.is_file()

    def _fail(self):
        if self.is_dir():
            raise ValueError(f"{self} is a directory, not a file")

        super()._fail()


class DirectoryPath(ValidPath):
    _validate = lambda self: self.is_dir()

    def _fail(self):
        if self.is_file():
            raise ValueError(f"{self} is a file, not a directory")

        super()._fail()
