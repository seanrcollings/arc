from typing import TypeVar, Generic, Generator

from . import ArcType

Start = TypeVar("Start")
End = TypeVar("End")


class Range(int, Generic[Start, End], ArcType):
    def __new__(cls, value: int, smallest: int, biggest: int):
        obj = int.__new__(Range, value)
        Range.__init__(obj, value, smallest, biggest)
        return obj

    def __init__(self, value, smallest: int, biggest: int):
        super().__init__()
        self.value = value
        self.smallest = smallest
        self.biggest = biggest

    def range(self):
        """Returns the result of `range(smallest, biggest)"""
        return range(self.smallest, self.biggest)

    def range_with_picked(self) -> Generator[tuple[int, bool], None, None]:
        """Iterator that returns each integer in the specified range, along
        with whether or not it was the value picked"""
        for i in self.range():
            yield i, i == self.value
