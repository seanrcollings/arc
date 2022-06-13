from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    from arc.autocompletions import Completion, CompletionInfo


Annotation = t.Union[t._SpecialForm, type]

NArgs = t.Union[int, t.Literal["+", "*"], None]

ParseResult = dict[str, t.Union[str, list[str], None]]

Env = t.Literal["production", "development"]

CommandName = t.Union[str, tuple[str], list[str], None]

InputArgs = t.Union[str, t.Sequence[str], None]

CompareReturn = t.Literal[-1, 0, 1]


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
