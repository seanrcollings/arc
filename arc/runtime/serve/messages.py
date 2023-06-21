import typing as t
from dataclasses import dataclass


@dataclass
class Exit:
    code: int = 0


@dataclass
class Close:
    ...


@dataclass
class Ping:
    ...


@dataclass
class Pong:
    ...


@dataclass
class Error:
    error: str


@dataclass
class RunCommand:
    command: str


@dataclass
class Output:
    output: str
    stream: t.Literal["stdout", "stderr"]


@dataclass
class CommandResult:
    result: t.Any


@dataclass
class Text:
    text: str


Message = (
    Exit | RunCommand | Text | Close | Ping | Pong | Output | CommandResult | Error
)
