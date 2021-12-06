from __future__ import annotations
import re
from functools import cached_property
from typing import Callable, Optional, Any, Union
from functools import cached_property

from arc import logging
from arc.color import effects, fg, colorize
from arc.result import Result
from arc.config import config
from arc.execution_state import ExecutionState

from .executable import Executable, FunctionExecutable, ClassExecutable


logger = logging.getArcLogger("command")
DEFAULT_SECTION: str = config.default_section_name


class Command:
    def __init__(
        self,
        name: str,
        executable: Callable,
        context: Optional[dict] = None,
        description: Optional[str] = None,
    ):
        self.name = name
        self.subcommands: dict[str, Command] = {}
        self.subcommand_aliases: dict[str, str] = {}
        self.context = context or {}
        self.doc = executable.__doc__ or description

        self.executable: Executable = (
            ClassExecutable(executable)
            if isinstance(executable, type)
            else FunctionExecutable(executable)
        )

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @property
    def function(self):
        return self.executable.wrapped

    def schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "doc": self.function.__doc__,
            "context": self.context,
            "subcommands": {
                name: command.schema() for name, command in self.subcommands.items()
            },
            "parameters": {
                name: param.schema() for name, param in self.executable.params.items()
            },
        }

    ### Execution ###

    def run(self, state: ExecutionState) -> Result:
        """External interface to execute a command"""
        return self.executable(state)

    ### Building Subcommands ###

    def subcommand(
        self,
        name: Union[str, list[str], tuple[str, ...]] = None,
        description: Optional[str] = None,
        context: dict[str, Any] = None,
    ):
        """Create and install a subcommands

        Args:
            name (Union[str, list[str], tuple[str, ...]], optional): The name to reference
                this subcommand by. Can optionally be a `list` of names. In this case,
                the first in the list will be treated as the "true" name, and the others
                will be treated as aliases. If no value is provided, `function.__name__` is used

            description(Optional[str]): Description of the command's function. Can be used
            to generate documentation.

            context (dict[str, Any], optional): Special data that will be
                passed to this command (and any subcommands) at runtime. Defaults to None.

        Returns:
            Command: the subcommand created
        """

        def decorator(wrapped: Union[Callable, Command]):
            if isinstance(wrapped, Command):
                wrapped = wrapped.executable.wrapped

            wrapped_name = wrapped.__name__
            if config.transform_snake_case:
                wrapped_name = wrapped_name.replace("_", "-")

            command_name = self.handle_command_aliases(name or wrapped_name)
            command = Command(command_name, wrapped, context or {}, description)
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
        from . import command_builders

        return self.function in (command_builders.no_op, command_builders.helper)

    ## Docstring
    @cached_property
    def parsed_docstring(self):
        """Parsed docstring for the command

        Sections are denoted by a new line, and
        then a line beginning with `#`. Whatever
        comes after the `#` will be the key in
        the sections dict. And all content between
        that `#` and the next `#` will be the value.

        The first section of the docstring is not
        required to possess a section header, and
        will be entered in as the `description` section.
        """
        parsed: dict[str, str] = {DEFAULT_SECTION: ""}
        if not self.doc:
            return {}

        lines = [line.strip() for line in self.doc.split("\n")]

        current_section = DEFAULT_SECTION

        for line in lines:
            if line.startswith("#"):
                current_section = line[1:].strip().lower()
                parsed[current_section] = ""
            else:
                parsed[current_section] += line + "\n"

        return parsed

    @property
    def description(self) -> Optional[str]:
        return self.parsed_docstring.get("description")

    @property
    def short_description(self) -> Optional[str]:
        description = self.description
        return description if description is None else description.split("\n")[0]

    @cached_property
    def _parsed_argument_section(self) -> Optional[dict[str, str]]:
        arguments = self.parsed_docstring.get("arguments")
        if not arguments:
            return None

        parsed: dict[str, str] = {}
        regex = re.compile(r"^\w+:.+")
        current_param = ""

        for line in arguments.splitlines():
            if regex.match(line):
                param, first_line = line.split(":")
                current_param = param
                parsed[current_param] = first_line.strip()
            elif current_param:
                parsed[current_param] += " " + line.strip()

        return parsed

    def update_param_descriptions(self):
        """Parses the function docstring, then updates
        paramaters with the associated description in the arguments section
        if the param does not have a description already.
        """
        descriptions = self._parsed_argument_section
        if not descriptions:
            return

        for param in self.executable.params.values():
            if not param.description:
                param.description = descriptions.get(param.arg_name)
