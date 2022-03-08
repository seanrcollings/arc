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
    res = (
        completions.complete()
        if completions.should_complete()
        else completions.source()
    )

    return res


def get_completions(obj: CompletionProtocol, info: CompletionInfo) -> list[Completion]:
    """Gets the completions for a particular object that supports the `CompletionProtocol`"""
    comps = obj.__completions__(info)
    if comps is None:
        comps = []
    elif not isinstance(comps, list):
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
        words = os.getenv("COMP_WORDS", "").split()[1:]
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

    def __init__(self, ctx: Context, info: CompletionInfo):
        self.ctx = ctx
        self.command = ctx.command
        self.info = info
        self.command_name = self.command.name or utils.discover_name().replace(".", "_")

    @property
    def completion_vars(self) -> dict:
        return {
            "name": self.command_name,
            "func_name": f"_{self.command_name}_completions".replace("-", "_"),
            "completion_var": self.completion_var,
        }

    @property
    def completion_var(self) -> str:
        return f"_{self.command_name}_complete".upper().replace("-", "_")

    def should_complete(self) -> bool:
        return os.getenv(self.completion_var) is not None

    def source(self) -> str:
        """Returns the script for the paricular lanuage"""
        return self.template.format(**self.completion_vars)

    def complete(self) -> str:
        """Actually provides the completions"""

    def format_completion(self, comp: Completion) -> str:
        return ""


class BashCompletion(ShellCompletion):
    name = "bash"
    template = """\
{func_name}() {{
    local completions;
    local IFS=" ";

    completions=$(env COMP_WORDS="${{COMP_WORDS[*]}}" COMP_CURRENT="${{COMP_WORDS[COMP_CWORD]}}" python manage.py --autocomplete bash)

    for comp in $completions; do
        IFS="|" read -r type value <<< "$comp"

        if [[ $type == "file" ]]; then
            compopt -o default
        elif [[ $type == "dir" ]]; then
            compopt -o dirnames
        elif [[ $type == "plain" ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}}

complete -o nosort -F {func_name} {name}
"""

    def complete(self) -> str:
        comps = get_completions(self.command, self.info)
        return " ".join([self.format_completion(comp) for comp in comps])

    def format_completion(self, comp: Completion) -> str:
        return f"{comp.type.value}|{comp.value}"


# class ZshCompletion(BashCompletion):
#     name = "zsh"
#     template = """\
# #compdef {func_name} {name}

# function {func_name} {{
#     local completions;
#     completions=$(env COMP_WORDS=${{COMP_POINT}} COMP_CURRENT=${{COMP_CWORD}} python manage.py --autocomplete zsh)

#     for comp in $completions; do

#     done

#     return 0
# }}
# """

#     def format_completion(self, comp: Completion) -> str:
#         string = f"{comp.type.value}|{comp.value}"
#         if comp.description:
#             string += f"[{comp.description}]"

#         return string


class FishCompletion(ShellCompletion):
    name = "fish"
    template = """\
function {func_name}
    set -l completions (env {completion_var}=true COMP_WORDS=(commandline -cp) COMP_CURRENT=(commandline -t) python manage.py --autocomplete fish)

    for comp in $completions
        set -l parsed (string split '|' $comp)
        set -l type $parsed[1]
        set -l data $parsed[2]

        switch $type
            case file
                __fish_complete_path $data
            case dir
                __fish_complete_directories $data
            case plain
                echo $data
            case '*'
                echo $data
        end

    end

end

complete -f -c {name} -a "({func_name})";
"""

    def complete(self) -> str:
        comps = get_completions(self.command, self.info)
        return "\n".join([self.format_completion(comp) for comp in comps])

    def format_completion(self, comp: Completion) -> str:
        string = f"{comp.type.value}|{comp.value}"
        if comp.description:
            string += f"\t{comp.description}"

        return string


shells = {"bash": BashCompletion, "fish": FishCompletion}
