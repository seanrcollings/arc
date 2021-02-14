import sys
from typing import List, Union, Optional

from arc.parser import parse
from arc import config, utils

from .color import effects
from .command import KeywordCommand, Command
from .errors import CommandError


class CLI(KeywordCommand):
    """The CLI class is now implemented as a subclass
    of the Command class and reality just acts as a
    conveneince wrapper around Command creation and
    the run function.

    :param arcfile: arc config file to load. defaults to ./.arc
    """

    def __init__(
        self, name="cli", function=utils.no_op, arcfile="./.arc", context=None
    ):
        super().__init__(name, function, context)
        config.load_arc_file(arcfile)

    # pylint: disable=arguments-differ
    def __call__(self, execute: Optional[str] = None):  # type: ignore
        return run(self, execute)

    def command(self, *args, **kwargs):
        return self.subcommand(*args, **kwargs)

    def execute(self, _):
        ...

    def match_input(self, _):
        ...

    def helper(self, level: int = 0):
        """Displays this help.
        """
        print(f"Usage: python3 {__file__} [COMMAND] [ARGUMENTS ...]\n\n")
        print(f"{effects.UNDERLINE}{effects.BOLD}Commands:{effects.CLEAR}\n")
        for command in self.subcommands.values():
            command.helper(level)


def run(
    command: Command, execute: Optional[str] = None, arcfile: Optional[str] = None,
):
    """Core function of the ARC API.
    Loads up the config file, parses the user input
    And then passes control over to the `command` object.

    :param command: command object to run
    :param execute: string to parse and execute. If it's not provided
    sys.argv will be used
    :param arcfile: file path to an arc config file to load
    """
    if arcfile:
        config.load_arc_file(arcfile)
    user_input: Union[List[str], str] = execute if execute else sys.argv[1:]
    command_node = parse(user_input)
    utils.logger.debug(command_node)
    with utils.handle(CommandError):
        return command.run(command_node)
