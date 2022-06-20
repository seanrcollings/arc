from __future__ import annotations
import typing as t
import os
import enum
import dataclasses as dc
from arc import errors
from arc.present.helpers import Joiner

if t.TYPE_CHECKING:
    from arc.context import Context
    from arc.typing import CompletionProtocol


def completions(shell: str, ctx: Context):

    info = CompletionInfo.from_env()
    if shell not in shells:
        raise errors.ArgumentError(
            f"Unsupported shell: {shell}. Supported shells: {Joiner.with_comma(shells)}"
        )
    comp: ShellCompletion = shells[shell](ctx, info)
    return comp.complete() if comp.should_complete() else comp.source()


def get_completions(
    obj: CompletionProtocol, info: CompletionInfo, *args, **kwargs
) -> list[Completion]:
    """Gets the completions for a particular object that supports the `CompletionProtocol`"""
    comps = obj.__completions__(info, *args, **kwargs)
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
    GROUPS = "groups"
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
        self.command_name = self.command.name

    @property
    def completion_vars(self) -> dict:
        return {
            "name_exe": "python cli.py"
            if os.getenv("ARC_DEVELOPMENT")
            else self.command_name,
            "name_com": self.command_name,
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
        return ""

    def format_completion(self, comp: Completion) -> str:
        return ""


class BashCompletion(ShellCompletion):
    name = "bash"
    template = """\
{func_name}() {{
    local completions;

    completions=$(env {completion_var}=true COMP_WORDS="${{COMP_WORDS[*]}}" \
        COMP_CURRENT="${{COMP_WORDS[COMP_CWORD]}}" {name} --autocomplete bash)

    while IFS= read -r comp; do
        IFS="|" read -r type value <<< "$comp"

        if [[ $type == "file" ]]; then
            compopt -o default
        elif [[ $type == "dir" ]]; then
            compopt -o dirnames
        elif [[ $type == "plain" ]]; then
            COMPREPLY+=($(compgen -W "$value" -- "${{COMP_WORDS[COMP_CWORD]}}"))
        fi

    done <<< "$completions"

    return 0
}}

complete -o nosort -F {func_name} {name}
"""

    def complete(self) -> str:
        comps = get_completions(self.command, self.info)
        return "\n".join([self.format_completion(comp) for comp in comps])

    def format_completion(self, comp: Completion) -> str:
        return f"{comp.type.value}|{comp.value}"


class ZshCompletion(BashCompletion):
    name = "zsh"
    template = """\
#compdef {name}

{func_name}() {{
    local -a completions;
    local -a array;

    completions=("${{(@f)$(env {completion_var}=true COMP_WORDS="${{words[*]}}" \
        COMP_CURRENT=${{words[$CURRENT]}} {name} --autocomplete zsh)}}")

    for comp in $completions; do
        parsed=(${{(@s/|/)comp}})
        type=${{parsed[1]}}
        value=${{parsed[2]}}

        if [[ "$type" == "dir" ]]; then
            _path_files -/
        elif [[ "$type" == "file" ]]; then
            _path_files -f
        elif [[ "$type" == "users" ]]; then
            _users
        elif [[ "$type" == "groups" ]]; then
            _groups
        elif [[ "$type" == "plain" ]]; then
            array+=("$value")
        fi
    done

    if [ -n "$array" ]; then
        compadd -U -V unsorted -a array
    fi
}}

compdef {func_name} {name};
"""

    def complete(self) -> str:
        comps = get_completions(self.command, self.info)
        return "\n".join([self.format_completion(comp) for comp in comps])

    def format_completion(self, comp: Completion) -> str:
        string = f"{comp.type.value}|{comp.value}"
        # if comp.description:
        #     string += f"[{comp.description}]"

        return string


class FishCompletion(ShellCompletion):
    name = "fish"
    template = """\
function {func_name}
    set -l completions (env {completion_var}=true COMP_WORDS=(commandline -cp) \
        COMP_CURRENT=(commandline -t) {name_exe} --autocomplete fish)

    for comp in $completions
        set -l parsed (string split '|' $comp)
        set -l type $parsed[1]
        set -l data $parsed[2]

        switch $type
            case file
                __fish_complete_path $data
            case dir
                __fish_complete_directories $data
            case users
                __fish_complete_users $data
            case groups
                __fish_complete_groups $data
            case plain
                echo $data
            case '*'
                echo $data
        end

    end

end

complete -f -c {name_com} -a "({func_name})";
"""

    def complete(self) -> str:
        comps = get_completions(self.command, self.info)
        return "\n".join([self.format_completion(comp) for comp in comps])

    def format_completion(self, comp: Completion) -> str:
        string = f"{comp.type.value}|{comp.value}"
        if comp.description:
            string += f"\t{comp.description}"

        return string


shells = {"bash": BashCompletion, "fish": FishCompletion, "zsh": ZshCompletion}
