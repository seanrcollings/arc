from typing import Optional, Union, Any
import sys
import shlex

from .errors import CommandError
from .command import Command
from .config import arc_config
from . import utils
from .color import fg, effects

# TODO: Get missing_command working
def run(
    command: Command, execute: Optional[str] = None, arcfile: Optional[str] = None,
):
    """Core function of the ARC API.
    Loads up the config file, parses the user input
    Finds the command referenced, then passes over control to it

    :param command: command object to run
    :param execute: string to parse and execute. If it's not provided
        `sys.argv` will be used
    :param arcfile: file path to an arc config file to load,
        will ignore if path does not exsit
    """
    if arcfile:
        arc_config.from_file(arcfile)

    user_input = get_input(execute)
    # How do we know if the command namespace is empty?
    command_namespace: list[str] = user_input[0].split(arc_config.namespace_sep)
    command_args: list[str] = user_input[1:]

    with utils.handle(CommandError):
        command, command_ctx = find_command(command, command_namespace)

        utils.logger.debug(
            "Executing command: %s%s%s",
            fg.YELLOW,
            ":".join(command_namespace),
            effects.CLEAR,
        )
        return command.run(command_namespace, command_args, command_ctx)


def get_input(execute: Optional[str]):
    user_input: Union[list[str], str] = execute if execute else sys.argv[1:]
    if isinstance(user_input, str):
        user_input = shlex.split(user_input)
    return user_input


def find_command(command: Command, command_namespace: list[str]):
    command_ctx = command.context
    for subcommand_name in command_namespace:
        if subcommand_name in command.subcommands:
            command = command.subcommands[subcommand_name]
        elif subcommand_name in command.subcommand_aliases:
            command = command.subcommands[command.subcommand_aliases[subcommand_name]]
        else:
            raise CommandError(
                f"The command {fg.YELLOW}"
                f"{':'.join(command_namespace)}{effects.CLEAR}{fg.RED} not found. "
                "Check --help for available commands"
            )

        command_ctx = command.context | command_ctx
    return command, command_ctx
