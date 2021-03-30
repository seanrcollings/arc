import sys
import os
import shlex
from arc import namespace as ns, CommandType as ct, Context

from ._autocomplete import AutoComplete

# TODO
# - Create a utils file for some helpful functions
# - change up the fish init so that the command also recieves the current cursor position
# - Use that current cursor position to determine if we should be providing subcommand auto completion
# - Come up with a better way to manage the difference between executing the autocomplte directly,
#     and the command line (use sed to cut the name of the command off?)


autocomplete = ns("_autocomplete")


@autocomplete.subcommand(command_type=ct.POSITIONAL)
def init(shell_name: str, ctx: Context):
    if shell_name == "fish":
        sys.stdout.write(
            f"complete -f -c {ctx.init['completions_for']} --arguments "
            f"'({ctx.init['completions_from']} _autocomplete:fish "
            f"command_str=(commandline))'"
        )
    elif shell_name == "bash":
        sys.stdout.write(
            f"complete -C '{ctx.init['completions_from']} _autocomplete:bash' "
            f"{ctx.init['completions_for']}"
        )


@autocomplete.subcommand()
def fish(command_str: str, ctx: Context):
    completer = AutoComplete(ctx.cli, command_str)
    completer.complete()
    print(*completer.completions, sep="\n")


@autocomplete.subcommand(command_type=ct.POSITIONAL)
def bash(ctx: Context, *args):
    completer = AutoComplete(ctx.cli, os.getenv("COMP_LINE", ""))
    completer.complete()
    print(*completer.completions, sep="\n")
