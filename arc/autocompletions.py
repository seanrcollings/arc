from __future__ import annotations
import typing as t
import os
import enum
import dataclasses as dc
from arc import utils
from arc._command import Command
from arc.context import Context


def completions(ctx: Context):
    info = CompletionInfo.from_env()
    completions = ShellCompletion(ctx, info)

    if info.empty():
        print(completions.source())
    else:
        print(completions.complete())


@dc.dataclass
class CompletionInfo:
    words: list[str]
    current: str

    def empty(self):
        return not self.words and not self.current

    @classmethod
    def from_env(cls) -> CompletionInfo:
        words = os.getenv("COMP_WORDS", "").split(" ")
        current = os.getenv("COMP_CURRNT", "")
        return cls(words, current)


class CompletionType(enum.Enum):
    FILE = "file"
    DIR = "dir"
    USERS = "users"
    PLAIN = "plain"


class Completion:
    def __init__(
        self,
        value: t.Any,
        type: CompletionType = CompletionType.PLAIN,
        description: str = None,
    ):
        self.value = value
        self.type = type
        self.description = description


class ShellCompletion:
    template: t.ClassVar[str]

    def __init__(self, ctx: Context, info: CompletionInfo):
        self.ctx = ctx
        self.command = ctx.command
        self.info = info

    @property
    def completion_vars(self) -> dict:
        return {
            "name": self.command.name or utils.discover_name(),
        }

    def source(self) -> str:
        """Returns the script for the paricular lanuage"""
        return self.template.format(**self.completion_vars)

    def complete(self) -> str:
        """Actually provides the completions"""


class BashCompletion:

    template = """\
_{name}_completion() {{
    local completions;

    completions=$(env COMP_WORDS=${{COMP_WORDS[*]}} COMP_CURRENT=${{COMP_CWORD}} {name} --autocomplete bash)

    for comp in $completions; do
        COMPREPLY+=($comp)
    done

    return 0
}}

complete -F _{name}_completions {name}
"""
