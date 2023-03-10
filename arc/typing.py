"""Module contains custom type defintions that arc uses"""
from __future__ import annotations

import typing as t

from arc.autocompletions import Completion, CompletionInfo

if t.TYPE_CHECKING:
    from arc.define.param import Param
    from arc.runtime import Context

T = t.TypeVar("T")

ExecEnv = dict[str, t.Any]

ExecMode = t.Literal["root", "subcommand"]

Annotation = t.Union[t._SpecialForm, type]

NArgs = t.Union[int, t.Literal["+", "*", "?"], None]

ParseResult = dict[str, t.Union[str, list[str], None]]

Env = t.Literal["production", "development", "test"]

InputArgs = t.Union[str, t.Sequence[str], None]

CompletionFunc = t.Callable[
    [CompletionInfo, "Param"], t.Union[list[Completion], Completion, None]
]

TypeMiddleware = t.Callable[[t.Any, "Context", "Param"], t.Any]

GetterFunc = t.Union[
    t.Callable[["Param", "Context"], t.Any],
    t.Callable[["Param"], t.Any],
    t.Callable[[], t.Any],
]


class ParamGroupOptions(t.TypedDict):
    exclude: t.Sequence[str] | None


@t.runtime_checkable
class ClassCallback(t.Protocol):
    def handle(self):
        ...


CommandCallback = t.Union[t.Callable, type[ClassCallback]]
"""The type of a command's callback.

May be a function
```py
@arc.command
def command(name: str):
    print(f"Hello {name}!")
```

Or a class
```py
@arc.command
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
