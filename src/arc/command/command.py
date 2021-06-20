from typing import Dict, Callable, Optional, Any, Type, Union, Collection
import functools

from arc.color import effects, fg
from arc.errors import CommandError, ExecutionError, NoOpError
from arc import utils

from .argument_parser import ArgumentParser, ParsingMethod


class CommandExecutor:
    def __init__(self, function: Callable):
        self.function = function

    @utils.timer("Command Execution")
    def execute(self, arguments: dict[str, Any]):
        BAR = "\u2500" * 40
        try:
            utils.logger.debug(BAR)
            return self.function(**arguments)
        except NoOpError as e:
            print(
                f"{fg.RED}This namespace cannot be executed. "
                f"Check --help for possible subcommands{effects.CLEAR}"
            )
        except ExecutionError as e:
            print(e)
        finally:
            utils.logger.debug(BAR)


# TODO
# - Function cleanup
# - @base
# - Context
class Command:
    def __init__(
        self,
        name: str,
        function: Callable,
        parser: Type[ArgumentParser],
        context: Optional[Dict] = None,
    ):
        self.name = name
        self.subcommands: Dict[str, Command] = {}
        self.subcommand_aliases: dict[str, str] = {}
        self.context: dict[str, Any] = context or {}
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

    def run(self, cli_args: list[str]):
        """External interface to execute a command"""
        args = self.parser.parse(cli_args)
        return self.executor.execute(args)

    ### Building Subcommands ###

    def subcommand(
        self,
        name: Union[str, list[str], tuple[str, ...]] = None,
        parsing_method: type[ArgumentParser] = None,
        **kwargs,
    ):
        """Create and install a subcommand

        Fallback for parsing_method:
          - provided argument
          - type of `self.parser`
        """

        parsing_method = parsing_method or type(self.parser)

        @self.ensure_function
        def decorator(function):
            command_name = self.handle_command_aliases(name or function.__name__)
            command = Command(command_name, function, parsing_method, **kwargs)
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

    def install_commands(self, *commands):
        return tuple(self.install_command(command) for command in commands)

    def install_command(self, command: "Command"):
        """Installs a command object as a subcommand
        of the current object"""
        command.propagate_context(self.context)
        self.subcommands[command.name] = command

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

    def propagate_context(self, new_context):
        self.context = (new_context or {}) | self.context
        for command in self.subcommands.values():
            command.propagate_context(self.context)

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
