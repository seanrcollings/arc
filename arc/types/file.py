from typing import TypeVar, Generic
from . import ArcType

T = TypeVar("T")

# Files do not work yet
class File(Generic[T], ArcType):
    READ = TypeVar("READ")
    WRITE = TypeVar("WRITE")
    APPEND = TypeVar("APPEND")
    CREATE = TypeVar("CREATE")

    __type_mappings = {
        READ: "r",
        WRITE: "w",
        APPEND: "a",
        CREATE: "x",
    }

    def __init__(self, file_path, modes):
        self.file_path = file_path
        self.mode = self.__type_mappings[modes[0]]
        self.__file_handle = None

    def __enter__(self):
        if not self.__file_handle:
            self.open()
        return self

    def __exit__(self, exception_type, value, traceback):
        print("exit")
        self.close()

    def __getattr__(self, attr):
        return getattr(self.__file_handle, attr)

    def close(self):
        if self.__file_handle:
            self.__file_handle.close()

    def __del__(self):
        if self.__file_handle:
            self.close()
        del self

    def open(self, mode=None):
        if self.__file_handle:
            self.close()

        mode = mode or self.mode

        self.__file_handle = open(self.file_path, mode)
        return self
