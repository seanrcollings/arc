from typing import TypeVar
from .arc_generic import ArcGeneric

T = TypeVar("T")

# Files do not work yet
class File(ArcGeneric[T]):
    READ = TypeVar("READ")
    WRITE = TypeVar("WRITE")
    APPEND = TypeVar("APPEND")

    __type_mappings = {
        READ: "r",
        WRITE: "w",
        APPEND: "A",
    }

    def __init__(self, file_path, modes):
        self.file_path = file_path
        self.mode = self.__type_mappings[modes[0]]
        self.__file_handle = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exception_type, value, traceback):
        self.__file_handle.close()

    def __getattr__(self, attr):
        return getattr(self.__file_handle, attr)

    def __del__(self):
        if self.__file_handle:
            self.__file_handle.close()

    def open(self):
        self.__file_handle = open(self.file_path, self.mode)
        return self
