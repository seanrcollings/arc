import sys
from arc import namespace, CommandType as ct, Context
from arc.command import Command
from arc.parser import parse


def maybe_break(buffer):
    if not buffer:
        return breakpoint
    else:
        return lambda: ...


autocomplete = namespace("_autocomplete")


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
    command: Command = ctx.cli
    namespace: list[str] = []
    for name in node.namespace:
        if name in command.subcommands:
            namespace.append(name)
            command = command.subcommands[name]
        else:
            break

    maybe_break(buffer)()

    for name, option in command.args.items():
        if option.annotation == bool:
            print(f"--{name}\t FLAG")
        else:
            print(f"{name}=\t{option.annotation}")

    # maybe_break(buffer)()
    if len(node.args) == 0:
        for name, subcommand in command.subcommands.items():
            if name in ("autocomplete", "help"):
                continue

            name = f"{':'.join(namespace)}:{name}" if len(namespace) > 0 else name
            print(f"{name}\t{subcommand.doc}")
