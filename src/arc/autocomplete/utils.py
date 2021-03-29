from arc.command import Command


def is_empty(lst: list[str]):
    return len(lst) == 0 or (len(lst) == 1 and lst[0] == "")


def maybe_break(shell):
    if not shell:
        return breakpoint
    else:
        return lambda: ...


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
