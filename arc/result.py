from typing import Generic, Optional, Type, TypeVar, Union
from abc import ABC, abstractmethod


T = TypeVar("T")


class _ResultBase(ABC, Generic[T]):
    def __init__(self, value: T = None):
        self.__value = value

    def unwrap(self):
        return self.__value

    @property
    @abstractmethod
    def ok(self):
        ...

    @property
    @abstractmethod
    def err(self):
        ...


class Ok(_ResultBase[T]):
    @property
    def ok(self):
        return True

    @property
    def err(self):
        return False


class Err(_ResultBase[T]):
    @property
    def ok(self):
        return False

    @property
    def err(self):
        return True


O = TypeVar("O")
E = TypeVar("E")


Result = Union[Ok[O], Err[E]]
