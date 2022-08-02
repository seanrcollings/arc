from __future__ import annotations
import typing as t

from arc.autocompletions import CompletionInfo, Completion

if t.TYPE_CHECKING:
    from arc.context import Context
    from arc._command.param import Param


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

GetterFunc = t.Callable[["Context", "Param"], t.Any]


@t.runtime_checkable
class ClassCallback(t.Protocol):
    def handle(self):
        ...


CommandCallback = t.Union[t.Callable, type[ClassCallback]]


class CompletionProtocol(t.Protocol):
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


class Suggestions(t.TypedDict, total=False):
    distance: int
    suggest_params: bool
    suggest_commands: bool


T = t.TypeVar("T")
MiddlewareCallable = t.Callable[[T], T]

DecoratorFunc = t.Callable[["Context"], t.Optional[t.Generator[None, t.Any, None]]]
ErrorHandlerFunc = t.Callable[[Exception, "Context"], None]
