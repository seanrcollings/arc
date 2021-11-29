from typing import Generic, TypeVar, Union
from abc import ABC, abstractmethod


T = TypeVar("T")


class _ResultBase(ABC, Generic[T]):
    def __init__(self, value: T = None):
        self._value = value

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self._value!r}>"

    def __eq__(self, other):
        return self._value == other._value

    def unwrap(self):
        return self._value

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
