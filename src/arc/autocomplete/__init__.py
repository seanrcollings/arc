import sys
from arc import namespace as ns, CommandType as ct, Context, ExecutionError

from ._autocomplete import AutoComplete, FishFormatter

autocomplete = ns("_autocomplete")


@autocomplete.subcommand(command_type=ct.POSITIONAL)
def init(shell_name: str, ctx: Context):
    if shell_name == "fish":
        sys.stdout.write(
            f"complete -f -c {ctx.init['completions_for']} --arguments "
            f"'({ctx.init['completions_from']} _autocomplete:fish "
            f"command_str=(commandline))'"
        )
    # elif shell_name == "bash":
    #     sys.stdout.write(
    #         f"complete -C '{ctx.init['completions_from']} _autocomplete:bash' "
    #         f"{ctx.init['completions_for']}"
    #     )
    else:
        raise ExecutionError("Autocompletion currently only supported in fish")


@autocomplete.subcommand()
def fish(command_str: str, ctx: Context):
    completer = AutoComplete(ctx.cli, command_str, FishFormatter)
    completer.complete()
    print(completer.display())


# @autocomplete.subcommand(command_type=ct.POSITIONAL)
# def bash(*args, ctx: Context):
#     completer = AutoComplete(ctx.cli, os.getenv("COMP_LINE", ""))
#     completer.complete()
#     print(*(completion.value for completion in completer.completions), sep="\n")
