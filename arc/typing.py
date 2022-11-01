"""Module contains custom type defintions that arc uses"""
from __future__ import annotations
import typing as t

from arc.autocompletions import CompletionInfo, Completion

if t.TYPE_CHECKING:
    from arc.context import Context
    from arc.core.param import Param

T = t.TypeVar("T")

ExecEnv = dict[str, t.Any]

ExecMode = t.Literal["global", "single", "subcommand"]

Annotation = t.Union[t._SpecialForm, type]

NArgs = t.Union[int, t.Literal["+", "*", "?"], None]

ParseResult = dict[str, t.Union[str, list[str], None]]

Env = t.Literal["production", "development"]

CommandName = t.Union[str, t.Sequence[str], None]

InputArgs = t.Union[str, t.Sequence[str], None]

CompareReturn = t.Literal[-1, 0, 1]

CompletionFunc = t.Callable[
    [CompletionInfo, "Param"], t.Union[list[Completion], Completion, None]
]

GetterFunc = t.Callable[["Param"], t.Any]

MiddlewareCallable = t.Callable[[T], T]

DecoratorFunc = t.Callable[["Context"], t.Optional[t.Generator[None, t.Any, None]]]

ErrorHandlerFunc = t.Callable[[Exception, "Context"], None]


@t.runtime_checkable
class ClassCallback(t.Protocol):
    def handle(self):
        ...


CommandCallback = t.Union[t.Callable, type[ClassCallback]]
"""The type of a command's callback.

May be a function
```py
@arc.command()
def command(name: str):
    print(f"Hello {name}!")
```

Or a class
```py
@arc.command()
class command:
    name: str

    def handle(self):
        print(f"Hello {self.name}!")

```
"""


class CompletionProtocol(t.Protocol):
    """Protocal that objects need to implement if they are expected to provide completions"""

    def __completions__(
        self, info: CompletionInfo, *args, **kwargs
    ) -> list[Completion] | Completion | None:
        ...


@t.runtime_checkable
class TypeProtocol(t.Protocol):
    """Protocol that custom types need to conform to"""

    @classmethod
    def __convert__(cls, value, *args):
        ...


class Suggestions(t.TypedDict):
    distance: int
    suggest_params: bool
    suggest_commands: bool
