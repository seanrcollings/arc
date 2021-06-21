from typing import Dict, Callable, Optional, Any, Type, Union
import functools

from arc.color import effects, fg
from arc.errors import CommandError
from arc import utils

from .argument_parser import ArgumentParser, ParsingMethod
from .command_executor import CommandExecutor

# TODO
# - Function cleanup
class Command:
    def __init__(
        self,
        name: str,
        function: Callable,
        parser: Type[ArgumentParser] = ParsingMethod.KEYWORD,
        context: Optional[Dict] = None,
    ):
        self.name = name
        self.subcommands: Dict[str, Command] = {}
        self.subcommand_aliases: dict[str, str] = {}
        self.context = context or {}
        self.doc = function.__doc__

        self.parser: ArgumentParser = parser(function)
        self.executor = CommandExecutor(function)

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @property
    def function(self):
        return self.executor.function

    @function.setter
    def function(self, func: Callable):
        self.parser.build_args(func)
        self.executor.function = func
        self.doc = func.__doc__

    ### Execution ###

    def run(
        self, _cli_namespace: list[str], cli_args: list[str], context: dict[str, Any]
    ):
        """External interface to execute a command"""
        self.context = context | self.context
        args = self.parser.parse(cli_args, self.context)
        return self.executor.execute(args)

    ### Building Subcommands ###

    def subcommand(
        self,
        name: Union[str, list[str], tuple[str, ...]] = None,
        parsing_method: type[ArgumentParser] = None,
        context: dict[str, Any] = None,
    ):
        """Create and install a subcommand

        Fallback for parsing_method:
          - provided argument
          - type of `self.parser`
        """

        parsing_method = parsing_method or type(self.parser)
        context = context or {}

        @self.ensure_function
        def decorator(function):
            command_name = self.handle_command_aliases(name or function.__name__)
            command = Command(command_name, function, parsing_method, context)
            return self.install_command(command)

        return decorator

    def base(self):
        """Decorator to replace the function
        of the current command"""

        @self.ensure_function
        def decorator(function):
            self.function = function
            return self

        return decorator

    def install_commands(self, *commands):
        return tuple(self.install_command(command) for command in commands)

    def install_command(self, command: "Command"):
        """Installs a command object as a subcommand
        of the current object"""
        self.subcommands[command.name] = command
        command.executor.register_callbacks(**self.executor.callbacks)

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

    ### Helpers ###

    def handle_command_aliases(
        self, command_name: Union[str, list[str], tuple[str, ...]]
    ) -> str:
        if isinstance(command_name, str):
            return command_name

        name = command_name[0]
        aliases = command_name[1:]

        for alias in aliases:
            self.subcommand_aliases[alias] = name

        return name

    @staticmethod
    def ensure_function(wrapped):
        """Decorator to insure that multiple commands
        can be created for the same function.
        """

        @functools.wraps(wrapped)
        def decorator(maybe_function):
            if isinstance(maybe_function, Command):
                # pylint: disable=protected-access
                return wrapped(maybe_function.function)
            if callable(maybe_function):
                return wrapped(maybe_function)

            raise CommandError(
                f"{wrapped.__name__} expected a function or "
                f"Command but recieved a {type(maybe_function)}"
            )

        return decorator
