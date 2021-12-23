from __future__ import annotations
import re
import typing as t
from arc.color import effects, fg
from arc.config import config

from arc import errors, utils, constants
from arc.context import Context

if t.TYPE_CHECKING:
    from .command import Command
    from .param import Param


def get_all_commands(
    command: Command, parent_namespace: str = "", root=True
) -> list[tuple[Command, str]]:
    """Recursively walks down the command tree, retrieves each command
    and generates fully-qualified names for all commands

    Args:
        command (Command): Root of the command tree you want to generates
        parent_namespace (str, optional): Parent namespace of `command`. Defaults to "".
        root (bool, optional): Whether or not the consider `command` the root of the namespace.
            Defaults to True.

    Returns:
        list[tuple[Command, str]]: List of commands and their fully-qualified names
    """
    if root:
        current_name = ""
    else:
        current_name = constants.NAMESPACE_SEP.join(
            (parent_namespace, command.name)
        ).lstrip(constants.NAMESPACE_SEP)

    commands = [(command, current_name)]

    for subcommand in command.subcommands.values():
        commands += get_all_commands(subcommand, current_name, False)

    return commands


def get_all_command_names(*args, **kwargs) -> list[str]:
    """Helper function that only returns the names from `get_all_commands`"""
    return list(name for command, name in get_all_commands(*args, **kwargs))


def find_command_chain(
    command: Command, command_namespace: list[str], ctx: Context
) -> list[Command]:
    """Walks down the subcommand tree using the proveded list of `command_namespace`.
    As it traverses the tree, it merges each levels context together, which will result
    in the final context to pass to the command in the end.

    When it hits the bottom of the `command_namespace` list
    (so long as none of them were invalid namespaces) it has found the called command
    and will return it.
    """
    command_chain = [command]

    for subcommand_name in command_namespace:
        if subcommand_name in command.subcommands:
            command = command.subcommands[subcommand_name]
            command_chain.append(command)
        elif subcommand_name in command.subcommand_aliases:
            command = command.subcommands[command.subcommand_aliases[subcommand_name]]
            command_chain.append(command)
        else:
            message = (
                f"The command {fg.YELLOW}"
                f"{':'.join(command_namespace)}{effects.CLEAR} not found. "
                f"Check {fg.BLUE}--help{effects.CLEAR} for available commands"
            )

            if ctx.suggestions["suggest_commands"] and (
                possible_command := find_similar_command(
                    command, command_namespace, ctx.suggestions["levenshtein_distance"]
                )
            ):
                message += f"\n\tPerhaps you meant {fg.YELLOW}{possible_command}{effects.CLEAR}?"

            raise errors.CommandNotFound(message)

    return command_chain


def find_similar_command(
    command: Command, namespace_list: list[str], distance: int
) -> str | None:
    """Finds commands in the command tree that resemble `namespace_list`
    Compares each of their full-qualified names to the provided name with
    the levenshtein algorithm. If it's similar enough (with respect to)
    `config.suggest_levenshtein_distance`, that command_name will be returned
    """

    namespace_str = constants.NAMESPACE_SEP.join(namespace_list)
    command_names = get_all_command_names(command)

    cur_dis, command_name = min(
        (
            (utils.levenshtein(namespace_str, command_name), command_name)
            for command_name in command_names
        ),
        key=lambda tup: tup[0],
    )

    if cur_dis <= distance:
        return command_name

    return None


namespace_seperated = re.compile(
    fr"\A\b((?:(?:{utils.IDENT}{constants.NAMESPACE_SEP})+"
    fr"{utils.IDENT})|{utils.IDENT}:?)$"
)


def get_command_namespace(string: str):
    if namespace_seperated.match(string):
        return string.split(constants.NAMESPACE_SEP)


# TODO: this will only ever return one possibility
def find_possible_params(
    params: list[Param], missing: str, distance: int
) -> list[Param]:
    filtered = []
    if len(params) > 0:
        cur_dis, param = min(
            ((utils.levenshtein(param.arg_alias, missing), param) for param in params),
            key=lambda tup: tup[0],
        )
        if cur_dis <= distance:
            filtered.append(param)

    return filtered
