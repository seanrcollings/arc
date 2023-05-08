from collections import UserList
import typing as t


class Constant:
    def __init__(self, name: str) -> None:
        self.__name = name

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return self.__name


MISSING = Constant("MISSING")
MISSING_DEFAULT = Constant("MISSING_DEFAULT")


COLLECTION_TYPES = (list, set, tuple, UserList)
