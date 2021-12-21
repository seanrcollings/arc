from __future__ import annotations
from typing import TYPE_CHECKING
import enum

from arc import command, Context
from arc.autocomplete import fish

if TYPE_CHECKING:
    from arc.cli import CLI


class AutocompleteContext(Context):
    cli: CLI
    init: dict[str, str]


class Shell(enum.Enum):
    FISH = "fish"


@command()
def autocomplete(shell: Shell, ctx: AutocompleteContext):
    """Provided shell autocompletion support"""
    exec_name = ctx.init["completions_for"]
    completions: str = ""
    if shell == Shell.FISH:
        completions = fish.generate(exec_name, ctx.cli)

    print(completions)
