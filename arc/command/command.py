from typing import Dict, Callable, Optional, Any, Union
import pprint
import logging

from arc.color import effects, fg
from arc import utils
from arc.result import Result
from arc.config import config
from arc.execution_state import ExecutionState

from .argument_parser import ArgumentParser
from .command_doc import CommandDoc
from .executable import Executable, FunctionExecutable, ClassExecutable


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

    def doc(self, state: ExecutionState) -> CommandDoc:
        doc = CommandDoc(
            self.function.__doc__ or "",
            state,
            ("usage",),
        )
        return doc

    ### Execution ###

    def run(self, state: ExecutionState) -> Result:
        """External interface to execute a command"""
        parsed_args = self.parser.parse(state.command_args)

        logger.debug("Parser Result: %s", pprint.pformat(parsed_args))
        state.parsed = parsed_args
        return self.executable(state)

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

        def decorator(wrapped: Union[Callable, Command]):
            if isinstance(wrapped, Command):
                wrapped = wrapped.executable.wrapped

            wrapped_name = wrapped.__name__
            if config.tranform_snake_case:
                wrapped_name = wrapped_name.replace("_", "-")

            command_name = self.handle_command_aliases(name or wrapped_name)
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

    def is_namespace(self):
        return self.function is utils.no_op
