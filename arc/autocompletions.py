from __future__ import annotations
from contextlib import redirect_stderr

import dataclasses as dc
import os
import typing as t

from arc import errors
from arc.present.joiner import Join

if t.TYPE_CHECKING:
    from arc.typing import CompletionProtocol
    from arc.define.command import Command


def get_completions(
    obj: CompletionProtocol,
    info: CompletionInfo,
    *args: t.Any,
    **kwargs: t.Any,
) -> list[Completion]:
    """Gets the completions for a particular object that supports the `CompletionProtocol`"""
    comps = obj.__completions__(info, *args, **kwargs)
    if comps is None:
        comps = []
    else:
        comps = list(comps)
    return comps


@dc.dataclass
class CompletionInfo:
    words: list[str]
    current: str

    def empty(self) -> bool:
        return not self.words and not self.current

    @classmethod
    def from_env(cls) -> CompletionInfo:
        words = os.getenv("COMP_WORDS", "").split()[1:]
        current = os.getenv("COMP_CURRENT", "")
        return cls(words, current)


class CompletionType:
    """Constants for common completion types"""

    FILE = "file"
    DIR = "dir"
    USERS = "users"
    GROUPS = "groups"
    PLAIN = "plain"


@dc.dataclass
class Completion:
    value: t.Any
    description: t.Optional[str] = None
    type: str = CompletionType.PLAIN
    data: dict[str, t.Any] = dc.field(default_factory=dict)


class ShellCompletion:
    template: t.ClassVar[str]
    shells: dict[str, type["ShellCompletion"]] = {}

    def __init__(self, command: Command, info: CompletionInfo):
        self.command = command
        self.info = info
        self.command_name = self.command.name

    def __init_subclass__(cls, name: str) -> None:
        ShellCompletion.shells[name] = cls

    @property
    def completion_vars(self) -> dict[str, t.Any]:
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

    @classmethod
    def run(cls, shell: str, command: Command) -> str:
        info = CompletionInfo.from_env()
        if shell not in cls.shells:
            raise errors.ArgumentError(
                f"Unsupported shell: {shell}. "
                f"Supported shells: {Join.with_comma(cls.shells)}"
            )
        comp: ShellCompletion = cls.shells[shell](command, info)

        with open("completions.log", "w+") as f, redirect_stderr(f):
            res = comp.complete() if comp.should_complete() else comp.source()
            f.write("\n")
            f.write(" ".join(info.words))
            f.write("\n")
            f.write(res)
            f.write("\n\n")

        return res


class BashCompletion(ShellCompletion, name="bash"):
    template = """\
{func_name}() {{
    local completions;

    completions=$(env {completion_var}=true COMP_WORDS="${{COMP_WORDS[*]}}" \
        COMP_CURRENT="${{COMP_WORDS[COMP_CWORD]}}" {name_exe} --autocomplete bash)

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

complete -o nosort -F {func_name} {name_exe}
"""

    def complete(self) -> str:
        comps = get_completions(self.command, self.info)
        return "\n".join([self.format_completion(comp) for comp in comps])

    def format_completion(self, comp: Completion) -> str:
        return f"{comp.type}|{comp.value}"


class ZshCompletion(BashCompletion, name="zsh"):
    template = """\
#compdef {name_exe}

{func_name}() {{
    local -a completions;
    local -a array;

    completions=("${{(@f)$(env {completion_var}=true COMP_WORDS="${{words[*]}}" \
        COMP_CURRENT=${{words[$CURRENT]}} {name_exe} --autocomplete zsh)}}")

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

compdef {func_name} {name_exe};
"""

    def complete(self) -> str:
        comps = get_completions(self.command, self.info)
        return "\n".join([self.format_completion(comp) for comp in comps])

    def format_completion(self, comp: Completion) -> str:
        string = f"{comp.type}|{comp.value}"
        # if comp.description:
        #     string += f"[{comp.description}]"

        return string


class FishCompletion(ShellCompletion, name="fish"):
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
        string = f"{comp.type}|{comp.value}"
        if comp.description:
            string += f"\t{comp.description}"

        return string
