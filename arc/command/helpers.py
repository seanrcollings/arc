from __future__ import annotations
from typing import TYPE_CHECKING
from arc import utils
from arc.config import config


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
