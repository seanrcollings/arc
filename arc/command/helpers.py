from __future__ import annotations
import re
from typing import TYPE_CHECKING
from arc.color import effects, fg
from arc.config import config

from arc import errors, utils

if TYPE_CHECKING:
    from .command import Command


def find_similar_command(command: Command, namespace_list: list[str]) -> str | None:
    """Finds commands in the command tree that resemble `namespace_list`
    Compares each of their full-qualified names to the provided name with
    the levenshtein algorithm. If it's similar enough (with respect to)
    `config.suggest_levenshtein_distance`, that command_name will be returned
    """
    if config.suggest_on_missing_command:
        namespace_str = config.namespace_sep.join(namespace_list)
        command_names = get_all_command_names(command)

        distance, command_name = min(
            (
                (utils.levenshtein(namespace_str, command_name), command_name)
                for command_name in command_names
            ),
            key=lambda tup: tup[0],
        )

        if distance <= config.suggest_levenshtein_distance:
            return command_name

    return None


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
        current_name = config.namespace_sep.join(
            (parent_namespace, command.name)
        ).lstrip(config.namespace_sep)

    commands = [(command, current_name)]

    for subcommand in command.subcommands.values():
        commands += get_all_commands(subcommand, current_name, False)

    return commands


def get_all_command_names(*args, **kwargs) -> list[str]:
    """Helper function that only returns the names from `get_all_commands`"""
    return list(name for command, name in get_all_commands(*args, **kwargs))


def find_command_chain(command: Command, command_namespace: list[str]) -> list[Command]:
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
            if possible_command := find_similar_command(command, command_namespace):
                message += f"\n\tPerhaps you meant {fg.YELLOW}{possible_command}{effects.CLEAR}?"

            raise errors.CommandError(message)

    return command_chain


namespace_seperated = re.compile(
    fr"\A\b((?:(?:{utils.IDENT}{config.namespace_sep})+"
    fr"{utils.IDENT})|{utils.IDENT}:?)$"
)


def get_command_namespace(string: str):
    if namespace_seperated.match(string):
        return string.split(config.namespace_sep)
