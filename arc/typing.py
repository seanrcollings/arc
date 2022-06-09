from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    from arc.autocompletions import Completion, CompletionInfo


class ClassCallback(t.Protocol):
    def handle(self):
        ...


CommandCallback = t.Union[t.Callable, type[ClassCallback]]
Annotation = t.Union[t._SpecialForm, type]

NArgs = t.Union[int, t.Literal["+", "*"], None]

ParseResult = dict[str, t.Union[str, list[str], None]]


class CompletionProtocol(t.Protocol):
    def __completions__(
        self, info: CompletionInfo, *args, **kwargs
    ) -> list[Completion] | Completion | None:
        ...


Env = t.Literal["production", "development"]


@t.runtime_checkable
class TypeProtocol(t.Protocol):
    """Protocol that custom types need to conform to"""

    # name: t.ClassVar[t.Optional[str]]

    @classmethod
    def __convert__(cls, value, *args):
        ...

    # @classmethod
    # def __prompt__(cls, ctx, param):
    #     ...


CompareReturn = t.Literal[-1, 0, 1]


class Suggestions(t.TypedDict, total=False):
    distance: int
    suggest_params: bool
    suggest_commands: bool
