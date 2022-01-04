from __future__ import annotations
import typing as t
import os
import enum
import dataclasses as dc
from arc import utils, logging


if t.TYPE_CHECKING:
    from arc.context import Context
    from arc._command import Command
    from arc.typing import CompletionProtocol


logger = logging.getArcLogger("comp")


def completions(shell: str, ctx: Context):
    info = CompletionInfo.from_env()
    completions: ShellCompletion = shells[shell](ctx, info)

    if info.empty():
        print(completions.source())
    else:
        print(completions.complete())


def get_completions(obj: CompletionProtocol, info: CompletionInfo) -> list[Completion]:
    """Gets the completions for a particular object that supports the `CompletionProtocol`"""
    comps = obj.__completions__(info)
    if not isinstance(comps, list):
        comps = [comps]
    return comps


@dc.dataclass
class CompletionInfo:
    words: list[str]
    current: str

    def empty(self):
        return not self.words and not self.current

    @classmethod
    def from_env(cls) -> CompletionInfo:
        words = os.getenv("COMP_WORDS", "").split()
        current = os.getenv("COMP_CURRENT", "")
        return cls(words, current)


class CompletionType(enum.Enum):
    FILE = "file"
    DIR = "dir"
    USERS = "users"
    PLAIN = "plain"


@dc.dataclass
class Completion:
    value: t.Any
    type: CompletionType = CompletionType.PLAIN
    description: t.Optional[str] = None
    data: dict = dc.field(default_factory=dict)


class ShellCompletion:
    template: t.ClassVar[str]
    name: t.ClassVar[str]
    supported_types: t.ClassVar[t.Optional[set[CompletionType]]] = None

    def __init__(self, ctx: Context, info: CompletionInfo):
        self.ctx = ctx
        self.command = ctx.command
        self.info = info

    @property
    def completion_vars(self) -> dict:
        return {
            "name": (self.command.name or utils.discover_name()).replace(".", "_"),
        }

    def source(self) -> str:
        """Returns the script for the paricular lanuage"""
        return self.template.format(**self.completion_vars)

    def complete(self) -> str:
        """Actually provides the completions"""

    def format_completion(self, comp: Completion) -> str:
        return ""

    @classmethod
    def _check_completion_type(cls, comp: Completion):
        if cls.supported_types is None:
            return

        if comp.type not in cls.supported_types:
            logger.warning(
                "%s not supported by %s completions",
                comp.type,
                cls.name,
            )


class BashCompletion(ShellCompletion):
    name = "bash"
    template = """\
_{name}_completions() {{
    local completions;

    completions=$(env COMP_WORDS=${{COMP_WORDS[*]}} COMP_CURRENT=${{COMP_CWORD}} {name} --autocomplete bash)

    for comp in $completions; do
        COMPREPLY+=($comp)
    done

    return 0
}}

complete -F _{name}_completions {name}
"""

    def complete(self) -> str:
        comps = [Completion(str(v), CompletionType.PLAIN) for v in range(10)]
        return " ".join([self.format_completion(comp) for comp in comps])

    def format_completion(self, comp: Completion) -> str:
        return f"{comp.type.value}|{comp.value}"


class FishCompletion(ShellCompletion):
    name = "fish"
    supported_types = {CompletionType.PLAIN}
    template = """\
function _{name}_completions
    set -l completions (env COMP_WORDS=(commandline -cp) COMP_CURRENT=(commandline -t) python manage.py --autocomplete fish)

    for comp in $completions
        set -l parsed (string split '|' $comp)
        set -l type $parsed[1]
        set data $parsed[2]

        switch $type
            # case file
            #     __fish_complete_path $data
            # case dir
            #     __fish_complete_directories $data
            case plain
                echo $data
            case '*'
                echo $data
        end

    end

end

complete -f -c {name} -a "(_cli_completions)";
"""

    def complete(self) -> str:
        comps = get_completions(self.command, self.info)
        return "\n".join([self.format_completion(comp) for comp in comps])

    def format_completion(self, comp: Completion) -> str:
        self._check_completion_type(comp)
        return f"{comp.type.value}|{comp.value}\t{comp.description}"


shells = {"bash": BashCompletion, "fish": FishCompletion}
