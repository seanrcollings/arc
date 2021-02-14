from abc import abstractmethod
from typing import List, Dict, Callable, Any
import textwrap

from arc import utils, config
from arc.color import effects, fg
from arc.errors import ExecutionError, CommandError, ValidationError
from arc.parser.data_types import CommandNode

from .__option import Option
from .helpers import ArgBuilder


class Command(utils.Helpful):
    """Abstract Commad Class, all Command types must inherit from it
    Helpful is abstract, so this is as well"""

    __name__: str

    def __init__(self, name: str, function: Callable, meta: Any = None):
        self.name = name
        self.function: Callable = function
        self.subcommands: Dict[str, Command] = {}

        self.args: Dict[str, Option] = self.build_args()
        self.meta = meta

        self.doc = None
        if (doc := self.function.__doc__) is not None:
            self.doc = textwrap.dedent(doc)

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    # CLI Builder Methods

    def subcommand(self, name=None, command_type=None, **kwargs):
        """decorator wrapper around install_script"""

        def decorator(function):
            command_name = name or function.__name__
            command = self.create_command(
                command_name, function, command_type, **kwargs
            )
            return self.install_command(command)

        return decorator

    def base(self):
        """Decorator to replace the function
        of the current command
        """

        def decorator(function):
            self.function = function
            if (doc := self.function.__doc__) is not None:
                self.doc = textwrap.dedent(doc)
            return self

        return decorator

    def create_command(self, name, function, command_type=None, **kwargs):
        """Creates a command object of provided command_type

        Fallback for command type:
          - provided arguement
          - command_type of the container (if it's a util it can also inherit
               it's type from it's parent)
          - Defaults to KEYWORD

        :returns: the Command object
        """
        from . import (  # pylint: disable=import-outside-toplevel
            command_factory,
            CommandType,
        )

        command_type = command_type or CommandType.get_command_type(self)
        command = command_factory(name, function, command_type, **kwargs)
        return command

    def install_command(self, command: "Command"):
        """Installs a command object as a subcommand
        of the current object"""
        self.subcommands[command.name] = command

        if "help" not in self.subcommands and self.name != "help":
            self.add_helper()

        utils.logger.debug(
            "%sregistered '%s' command to %s %s",
            fg.YELLOW,
            command.name,
            self.name,
            effects.CLEAR,
        )

        return command

    def build_args(self) -> Dict[str, Option]:
        """Builds the options and flag collections based
        on the function definition
        """
        with ArgBuilder(self.function) as builder:
            for idx, param in enumerate(builder):
                meta = builder.get_meta(index=idx)
                self.arg_hook(param, meta)

            return builder.args

    # Command Execution Methods

    def run(self, command_node: CommandNode):
        """External interface to execute a command"""
        if command_node.empty_namespace():
            return self.__execute(command_node)
        else:
            subcommand_name = command_node.namespace.pop(0)
            if subcommand_name not in self.subcommands:
                raise CommandError(f"The subcommand '{subcommand_name}' not found.")

            subcommand = self.subcommands[subcommand_name]
            return subcommand.run(command_node)

    def __execute(self, command_node):
        """functionality wrapped around
        the public execute. Called by
        the run function

        Handles a few things behind the scenes
            - calls self.validate_input
            - calls self.match_input
        Both of these can be defined in the
        children classes, and will never need to be called
        directly by the child class

        :param command_node: SciptNode object created by the parser
            May contain options, flags and arbitrary args

        """
        with utils.handle(ValidationError):
            self.validate_input(command_node)

        self.match_input(command_node)
        BAR = "\u2500" * 40
        try:
            utils.logger.debug(BAR)
            self.execute(command_node)
        except ExecutionError as e:
            print(e)
        finally:
            utils.logger.debug(BAR)

        self.cleanup()

    @abstractmethod
    def execute(self, command_node: CommandNode):
        """Execution entry point of each command

        :param command_node: SciptNode object created by the parser.
        None of the Command classes use command_node in their implementation
        of execute, but they may need to so it passes it currently
        """

    @abstractmethod
    def match_input(self, command_node: CommandNode) -> None:
        """Matches the input provided by command_node
        with the command's options and flags. Should mutate
        state because this function returns None. For example,
        options values should be set on their respective option
        in self.options

        :param command_node: ScriptNode object created by the parser
        Has had the UtilNode stripped away if it existed
        """

    def arg_hook(self, param, meta) -> None:
        """`build_args` hook.
        Can be used to check each of the args it's creating"""

    def validate_input(self, command_node) -> None:
        """Helper function to check if user input is valid,
        should be overridden by child class

        If it isn't valid, raise a `ValidationError`"""

    # Utils

    def cleanup(self):
        for arg in self.args.values():
            arg.cleanup()

    def add_helper(self):
        helper_command = self.create_command("help", self.helper)
        self.install_command(helper_command)

    def helper(self, level: int = 0):
        """helper doc"""
        sep = config.namespace_sep
        indent = "    " * level
        name = f"{fg.GREEN}{self.name}{effects.CLEAR}"
        if level == 0:
            print(textwrap.indent(name, indent))
        else:
            print(textwrap.indent(sep + name, indent))

        if self.doc:
            print(textwrap.indent(self.doc, indent + "  "))

        if len(self.subcommands) > 0:
            print(
                textwrap.indent(
                    f"{effects.BOLD}{effects.UNDERLINE}Subcomands:{effects.CLEAR}",
                    indent + "  ",
                )
            )
            for command in self.subcommands.values():
                if command.name != "help":
                    command.helper(level + 1)
