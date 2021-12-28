import typing as t

Annotation = t.Union[t._SpecialForm, type]


@t.runtime_checkable
class TypeProtocol(t.Protocol):
    """Protocol that custom types need to conform to"""

    # name: t.ClassVar[t.Optional[str]]

    @classmethod
    def __convert__(cls, value, *args):
        ...


CompareReturn = t.Literal[-1, 0, 1]


@t.runtime_checkable
class ClassCallback(t.Protocol):
    __name__: str

    def handle(self) -> t.Any:
        ...


CollectionTypes = (list, set, tuple)


class Suggestions(t.TypedDict, total=False):
    levenshtein_distance: int
    suggest_arguments: bool
    suggest_commands: bool


Env = t.Literal["development", "production"]
CallbackTime = t.Literal["before", "around", "after"]
