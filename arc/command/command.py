from typing import Dict, Callable, Optional, Any, Union, TYPE_CHECKING
import functools
import pprint
import logging

from arc.color import effects, fg
from arc.errors import CommandError
from arc import utils
from arc.result import Result

from .argument_parser import ArgumentParser
from .command_doc import CommandDoc
from .executable import Executable, FunctionExecutable, ClassExecutable

if TYPE_CHECKING:
    from arc.execution_state import ExecutionState


logger = logging.getLogger("arc_logger")


class Command:
    def __init__(
        self,
        name: str,
        executable: Callable,
        context: Optional[Dict] = None,
    ):
        self.name = name
        self.subcommands: Dict[str, Command] = {}
        self.subcommand_aliases: dict[str, str] = {}
        self.context = context or {}

        self.executable: Executable = (
            ClassExecutable(executable)
            if isinstance(executable, type)
            else FunctionExecutable(executable)
        )
        self.parser = ArgumentParser(self.executable)

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @property
    def function(self):
        return self.executable.wrapped

    def doc(self, state: "ExecutionState") -> CommandDoc:
        doc = CommandDoc(
            self.function.__doc__ or "",
            state,
            ("usage",),
        )
        return doc

    ### Execution ###

    def run(self, exec_state: "ExecutionState") -> Result:
        """External interface to execute a command"""
        parsed_args = self.parser.parse(exec_state.command_args)

        logger.debug("Parsed arguments: %s", pprint.pformat(parsed_args))
        return self.executable(parsed_args, exec_state)

    ### Building Subcommands ###

    def subcommand(
        self,
        name: Union[str, list[str], tuple[str, ...]] = None,
        context: dict[str, Any] = None,
    ):
        """Create and install a subcommands

        Args:
            name (Union[str, list[str], tuple[str, ...]], optional): The name to reference
                this subcommand by. Can optionally be a `list` of names. In this case,
                the first in the list will be treated as the "true" name, and the others
                will be treated as aliases. If no value is provided, `function.__name__` is used
            context (dict[str, Any], optional): Special data that will be
                passed to this command (and any subcommands) at runtime. Defaults to None.

        Returns:
            Command: the subcommand created
        """

        # @self.ensure_function
        def decorator(wrapped: Union[Callable, Command]):
            if isinstance(wrapped, Command):
                wrapped = wrapped.executable.wrapped

            command_name = self.handle_command_aliases(name or wrapped.__name__)
            command = Command(
                command_name,
                wrapped,
                context or {},
            )
            return self.install_command(command)

        return decorator

    def install_commands(self, *commands):
        return tuple(self.install_command(command) for command in commands)

    def install_command(self, command: "Command"):
        """Installs a command object as a subcommand
        of the current object"""
        self.subcommands[command.name] = command
        command.executable.callback_store.register_callbacks(
            **self.executable.callback_store.inheritable_callbacks()
        )

        logger.debug(
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

    def is_namespace(self):
        return self.function is utils.no_op
