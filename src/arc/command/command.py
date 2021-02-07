from abc import abstractmethod
from typing import List, Dict, Callable, Any
import re

from arc import config, utils
from arc.color import effects, fg
from arc.errors import ExecutionError, ScriptError, ValidationError
from arc.parser.data_types import CommandNode

from .__option import Option
from .command_mixin import CommandMixin


class Command(utils.Helpful, CommandMixin):
    """Abstract Commad Class, all Command types must inherit from it
    Helpful is abstract, so this is as well"""

    def __init__(self, name: str, function: Callable, meta: Any = None):
        self.name = name
        self.function: Callable = function
        self.subcommands: Dict[str, Command] = {}

        self.args = self.build_args()
        self.validation_errors: List[str] = []
        self.meta = meta

        self.doc = None
        if self.function.__doc__ is not None:
            doc = re.sub(r"\n\s+", "\n", self.function.__doc__)
            doc = re.sub(r"\n\t+", "\n", doc)
            self.doc = doc

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def subcommand(self, name=None, command_type=None, **kwargs):
        """decorator wrapper around install_script"""

        def decorator(function):
            command = self.create_command(name, function, command_type, **kwargs)
            return self.install_command(command)

        return decorator

    def base(self):
        """Decorator to replace the function
        of self
        """

        def decorator(function):
            self.function = function
            return self

        return decorator

    def create_command(self, name, function, command_type=None, **kwargs):
        """Creates a command object of provided command_type

        Fallback for script type:
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
        return command_factory(name, function, command_type, **kwargs)

    def install_command(self, command: "Command"):
        """Installs a command object as a subcommands
        of the current object"""
        self.subcommands[command.name] = command

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
        with self.ArgBuilder(self.function) as builder:
            for idx, param in enumerate(builder):
                meta = builder.get_meta(index=idx)
                self.arg_hook(param, meta)

            return builder.args

    def run(self, command_node: CommandNode):
        """External interface to execute a command"""
        if command_node.empty_namespace():
            return self.call_wrapper(command_node)
        else:
            subcommand_name = command_node.namespace.pop(0)
            if subcommand_name not in self.subcommands:
                raise ScriptError(f"The subcommand '{subcommand_name}' not found.")

            subcommand = self.subcommands[subcommand_name]
            return subcommand.run(command_node)

    def call_wrapper(self, command_node):
        """functionality wrapped around
        actually calling self.function

        Handles a few things behind the scenes
            - calls self.validate_input
            - calls self.match_input
        Both of these can be defined in the
        children classes, and will never need to be called
        directly by the child class

        :param command_node: SciptNode object created by the parser
            May contain options, flags and arbitrary args

        """
        try:
            self.validate_input(command_node)
        except ValidationError as e:
            self.validation_errors.append(str(e))

        if len(self.validation_errors) == 0:
            self.match_input(command_node)
            try:
                utils.logger.debug("---------------------------")
                self.execute(command_node)
            except ExecutionError as e:
                print(e)
            finally:
                utils.logger.debug("---------------------------")
        else:
            raise ScriptError(
                "Pre-script validation checks failed: \n",
                "\n".join(self.validation_errors),
            )

        self.cleanup()

    @abstractmethod
    def execute(self, command_node: CommandNode):
        """Execution entry point of each script

        :param command_node: SciptNode object created by the parser.
        None of the Script classes use command_node in their implementation
        of execute, but they may need to so it passes it currently
        """

    @abstractmethod
    def match_input(self, command_node: CommandNode) -> None:
        """Matches the input provided by command_node
        with the script's options and flags. Should mutate
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

    def cleanup(self):
        for option in self.args.values():
            option.cleanup()

    def helper(self):
        spaces = "  "
        print(
            utils.indent(
                f"{config.utility_seperator}{fg.GREEN}{self.name}{effects.CLEAR}",
                spaces,
            )
        )
        if self.doc:
            print(utils.indent(self.doc, spaces * 3))
        else:
            obj: utils.Helpful
            print(f"{spaces}Arguments:")
            for obj in self.args.values():
                print(spaces * 3, end="")
                obj.helper()
