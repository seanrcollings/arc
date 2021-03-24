import sys
from arc import namespace as ns, CommandType as ct, Context
from arc.command import Command
from arc.parser import parse, CommandNode

# TODO
# - Create a utils file for some helpful functions
# - change up the fish init so that the command also recieves the current cursor position
# - Use that current cursor position to determine if we should be providing subcommand auto completion
# - Come up with a better way to manage the difference between executing the autocomplte directly,
#     and the command line (use sed to cut the name of the command off?)


def maybe_break(buffer):
    if not buffer:
        return breakpoint
    else:
        return lambda: ...


autocomplete = ns("_autocomplete")


def current_namespace(
    command: Command, namespace: list[str]
) -> tuple[list[str], Command]:
    """Takes in a command object and navigates down
    it's subcommand tree via the namespace list,
    when a namespace isn't a valid subcommand,
    it will break out and return the last valid one"""
    curr_namespace: list[str] = []
    for name in namespace:
        if name in command.subcommands:
            curr_namespace.append(name)
            command = command.subcommands[name]
        else:
            break

    return curr_namespace, command


@autocomplete.subcommand(command_type=ct.POSITIONAL)
def init(shell_name: str, ctx: Context):
    if shell_name == "fish":
        sys.stdout.write(
            f"complete -f -c {ctx.init['completions_for']} --arguments "
            f"'({ctx.init['completions_from']} _autocomplete:fish command_str=(commandline -p) --buffer)'"
        )


@autocomplete.subcommand(context={"ends_in_space": sys.argv[-1][-1] == " "})
def fish(command_str: str, buffer: bool, ctx: Context):
    if buffer:
        strings = command_str.split(" ")[1:]
    else:
        strings = command_str.split(" ")

    maybe_break(buffer)()
    node = parse(strings)
    namespace, command = current_namespace(ctx.cli, node.namespace)
    maybe_break(buffer)()

    for name, option in command.args.items():
        if option.annotation == bool:
            print(f"--{name}\t FLAG")
        else:
            print(f"{name}=\t{option.annotation}")

    # maybe_break(buffer)()
    if len(node.args) == 0 and not ctx.ends_in_space:
        for name, subcommand in command.subcommands.items():
            if name in ("_autocomplete", "help"):
                continue

            name = f"{':'.join(namespace)}:{name}" if len(namespace) > 0 else name
            print(f"{name}\t{subcommand.doc}")
