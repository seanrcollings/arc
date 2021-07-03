from typing import Optional, Union, Any
import sys
import shlex
import re
import logging

from arc import utils
from .errors import CommandError
from .command import Command
from .config import config
from .color import fg, effects

logger = logging.getLogger("arc_logger")

namespace_seperated = re.compile(
    fr"\A\b((?:(?:{utils.IDENT}{config.namespace_sep})+"
    fr"{utils.IDENT})|{utils.IDENT}:?)$"
)


@utils.timer("Running")
def run(
    command: Command,
    execute: Optional[str] = None,
    arcfile: Optional[str] = None,
):
    """Core function of the ARC API.
    Loads up the config file, parses the user input
    Finds the command referenced, then passes over control to it

    Args:
        command (Command): command object to run
        execute (str): string to parse and execute. If it's not provided
            `sys.argv` will be used
        arcfile (str): file path to an arc config file to load,
            will ignore if path does not exsit
    """
    utils.header("EXECUTE")
    if arcfile:
        config.from_file(arcfile)

    user_input = get_input(execute)
    command_namespace, command_args = get_command_namespace(user_input)

    with utils.handle(CommandError):
        command, command_ctx = find_command(command, command_namespace)

        logger.debug(
            "Executing command: %s%s%s",
            fg.YELLOW,
            ":".join(command_namespace) or "root",
            effects.CLEAR,
        )
        return command.run(command_namespace, command_args, command_ctx)


def get_input(execute: Optional[str]) -> list[str]:
    """Retrieves the users' input.

    If `execute` is provided, it is split using shell-like syntax.
    If it is absent, `sys.argv` is returned
    """
    user_input: Union[list[str], str] = execute if execute else sys.argv[1:]
    if isinstance(user_input, str):
        user_input = shlex.split(user_input)
    return user_input


def get_command_namespace(
    user_input: list[str],
) -> tuple[list[str], list[str]]:
    """Checks to see if the first argument from the user is a valid
    namespace name. If it is not, it will return an emtpy namespace list and
    cli.missing_command will be executed.
    """
    if len(user_input) > 0:
        namespace = user_input[0]
        if namespace_seperated.match(namespace):
            namespace = namespace.replace("-", "_")
            return namespace.split(config.namespace_sep), user_input[1:]

    return [], user_input


def find_command(
    command: Command, command_namespace: list[str]
) -> tuple[Command, dict[str, Any]]:
    """Walks down the subcommand tree using the proveded list of `command_namespace`.
    As it traverses the tree, it merges each levels context together, which will result
    in the final context to pass to the command in the end.

    When it hits the bottom of the `command_namespace` list
    (so long as none of them were invalid namespaces) it has found the called command
    and will return it.
    """
    command_ctx = command.context
    for subcommand_name in command_namespace:
        if subcommand_name in command.subcommands:
            command = command.subcommands[subcommand_name]
        elif subcommand_name in command.subcommand_aliases:
            command = command.subcommands[command.subcommand_aliases[subcommand_name]]
        else:
            raise CommandError(
                f"The command {fg.YELLOW}"
                f"{':'.join(command_namespace)}{effects.CLEAR} not found. "
                f"Check {fg.BLUE}--help{effects.CLEAR} for available commands"
            )

        command_ctx = command.context | command_ctx
    return command, command_ctx
