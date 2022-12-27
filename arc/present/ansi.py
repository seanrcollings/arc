import typing as t
import re
import functools


class Ansi:
    def __init__(self, content: t.Any):
        self.__content = content

    def __str__(self):
        return f"\033[{self.__content}"

    @classmethod
    def clean(cls, string: str):
        """Gets rid of escape sequences"""
        return cls.__ansi_escape().sub("", string)

    @classmethod
    def len(cls, string: str) -> int:
        """Length of a string, not including escape sequences"""
        length = 0
        in_escape_code = False

        for char in string:
            if in_escape_code and char == "m":
                in_escape_code = False
            elif char == "\x1b" or in_escape_code:
                in_escape_code = True
            else:
                length += 1

        return length

    @classmethod
    @functools.cache
    def __ansi_escape(self):
        return re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
