from __future__ import annotations
from typing import TYPE_CHECKING
import enum

from arc import command, Context, ParsingMethod as pm
from arc.command import helpers

from . import fish

if TYPE_CHECKING:
    from arc.cli import CLI


class AutocompleteContext(Context):
    cli: CLI
    init: dict[str, str]


class Shell(enum.Enum):
    FISH = "fish"


@command(parsing_method=pm.POSITIONAL)
def autocomplete(shell: Shell, ctx: AutocompleteContext):
    exec_name = ctx.init["completions_for"]
    if shell == Shell.FISH:
        fish.generate(exec_name, ctx.cli)
