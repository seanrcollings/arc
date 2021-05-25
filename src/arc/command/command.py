from abc import abstractmethod
from typing import Dict, Callable, Optional, Tuple, Any
import textwrap
import functools


from arc import utils, arc_config
from arc.color import effects, fg
from arc.errors import CommandError, ValidationError
from arc.parser.data_types import CommandNode

from .__option import Option
from .helpers import ArgBuilder, FunctionWrapper


class Command(utils.Helpful):
    """Abstract Commad Class, all Command types must inherit from it
    Helpful is abstract, so this is as well"""

    __name__: str

    # Used to indicate that this command can be
    # autoladed by invoking cli.autoload(...)
    # is automatcially set when creating a
    # command via `namespace()`
    __autoload__: bool = False

    function = FunctionWrapper()
    _function: Any  # Set by the FunctionWrapper
    context: dict
    args: Dict[str, Option]

    # hidden_args are special argumetnts
    # that arc will inject into the
    # function call. These cannot be provided
    # by the execution string and are matched
    # by type annotation
    _hidden_args: Dict[str, Option]
    doc: Optional[str]

    def __init__(self, name: str, function: Callable, context: Optional[Dict] = None):
        self.name = name
        self.args = {}  # KeywordCommand Freaks out if this isn't here
        self.function = function
        self.subcommands: Dict[str, Command] = {}
        self.context = context or {}

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @property
    def hidden_args(self) -> dict:
        if context := self._hidden_args.get("context"):
            context.value = context.annotation(self.context)

        return dict({arg.name: arg.value for arg in self._hidden_args.values()})

    ### CLI Building ###

    def subcommand(self, name=None, command_type=None, **kwargs):
        """Create and install a subcommand"""

        @self.ensure_function
        def decorator(function):
            command_name = name or function.__name__
            command = self.create_command(
                command_name, function, command_type, **kwargs
            )
            return self.install_command(command)

        return decorator

    def base(self, context: Optional[dict] = None):
        """Decorator to replace the function
        of the current command"""

        @self.ensure_function
        def decorator(function):
            self.function = function
            self.propagate_context(context)
            return self

        return decorator

    def create_command(self, name, function, command_type=None, **kwargs):
        """Creates a command object of provided command_type

        Fallback for command type:
          - provided arguement
          - command_type of the parent namespace
          - KeywordCommand

        :returns: the Command object
        """
        from . import (  # pylint: disable=import-outside-toplevel
            command_factory,
            CommandType,
        )

        command_type = command_type or CommandType.get_command_type(self)
        command = command_factory(name, function, command_type, **kwargs)
        return command

    def install_commands(self, *commands):
        return tuple(self.install_command(command) for command in commands)

    def install_command(self, command: "Command"):
        """Installs a command object as a subcommand
        of the current object"""
        command.propagate_context(self.context)
        self.subcommands[command.name] = command

        if "help" not in self.subcommands and self.name != "help":
            self.add_helper()

        utils.logger.debug(
            "Registered %s%s%s command to %s%s%s",
            fg.YELLOW,
            command.name,
            effects.CLEAR,
            fg.YELLOW,
            self.name,
            effects.CLEAR,
        )

        return command

    def build_args(self) -> Tuple[Dict[str, Option], Dict[str, Option]]:
        """Builds the args and arc_args collections based
        on the function definition
        """
        with ArgBuilder(self.function) as builder:
            for idx, param in enumerate(builder):
                meta = builder.get_meta(index=idx)
                self.arg_hook(param, meta)

            return builder.args, builder.hidden_args

    ### Execution ###

    def run(self, command_node: CommandNode):
        """External interface to execute a command"""
        if command_node.empty_namespace():
            self.pre_execute(command_node)
            value = self.execute(command_node)
            return self.post_execute(value)

        else:
            subcommand_name = command_node.namespace.pop(0)
            if subcommand_name not in self.subcommands:
                raise CommandError(f"The subcommand '{subcommand_name}' not found.")

            subcommand = self.subcommands[subcommand_name]
            return subcommand.run(command_node)

    def pre_execute(self, command_node: CommandNode):
        """Pre Command Execution hook.
        By default, handles a few things behind the scenes
            - calls `validate_input`
            - calls `match_input`

        Both of these can be defined in the
        children classes, and will never need to be called
        directly by the child class"""

        with utils.handle(ValidationError):
            self.validate_input(command_node)

        self.match_input(command_node)

    @abstractmethod
    def execute(self, command_node: CommandNode):
        """Execution entry point of each command

        :param command_node: CommandNode object created by the parser.
        None of the Command classes use command_node in their implementation
        of execute, but they may need to so it passes it currently
        """

    def post_execute(self, value):
        """Post Command Execution Hook
        by default calls `cleanup` and
        returns the provided value

        :param value: return value of the command

        """
        self.cleanup()
        return value

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

    ### Helpers ###

    def propagate_context(self, new_context):
        self.context = (new_context or {}) | self.context
        for command in self.subcommands.values():
            command.propagate_context(self.context)

    def cleanup(self):
        for arg in self.args.values():
            arg.cleanup()

    def add_helper(self):
        helper_command = self.create_command("help", self.helper)
        self.install_command(helper_command)

    def helper(self, level: int = 0):
        """helper doc"""
        sep = arc_config.namespace_sep
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

    @staticmethod
    def ensure_function(wrapped):
        """Decorator to insure that multiple commands
        can be created for the same function.
        """

        @functools.wraps(wrapped)
        def decorator(maybe_function):
            if isinstance(maybe_function, Command):
                # pylint: disable=protected-access
                return wrapped(maybe_function._function)
            if callable(maybe_function):
                return wrapped(maybe_function)

            raise CommandError(
                f"{wrapped.__name__} expected a function or "
                f"Command but recieved a {type(maybe_function)}"
            )

        return decorator
