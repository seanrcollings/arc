from typing import Dict, Callable, Optional, Any, Type, Union
import functools
import pprint
import logging

from arc.color import effects, fg
from arc.errors import CommandError, ParserError
from arc import utils
from arc.result import Result

from .argument_parser import ArgumentParser, ParsingMethod
from .command_executor import CommandExecutor
from .command_doc import CommandDoc


logger = logging.getLogger("arc_logger")


class Command:
    _command_doc: Optional[CommandDoc] = None

    def __init__(
        self,
        name: str,
        function: Callable,
        parser: Type[ArgumentParser] = ParsingMethod.KEYWORD,
        context: Optional[Dict] = None,
        short_args=None,
    ):
        self.name = name
        self.subcommands: Dict[str, Command] = {}
        self.subcommand_aliases: dict[str, str] = {}
        self.context = context or {}

        self.parser: ArgumentParser = parser(function, short_args)
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

    @property
    def doc(self) -> CommandDoc:
        if not self._command_doc:
            self._command_doc = CommandDoc(self.function.__doc__ or "", ("usage",))

        return self._command_doc

    ### Execution ###

    def run(
        self, cli_namespace: list[str], cli_args: list[str], context: dict[str, Any]
    ):
        """External interface to execute a command"""
        self.context = context | self.context
        with utils.handle(ParserError):
            parsed_args = self.parser.parse(cli_args, self.context)

        logger.debug("Parsed arguments: %s", pprint.pformat(parsed_args))
        return self.executor.execute(cli_namespace, parsed_args)

    ### Building Subcommands ###

    def subcommand(
        self,
        name: Union[str, list[str], tuple[str, ...]] = None,
        parsing_method: type[ArgumentParser] = None,
        context: dict[str, Any] = None,
        short_args: dict[str, str] = None,
    ):
        """Create and install a subcommands

        Args:
            name (Union[str, list[str], tuple[str, ...]], optional): The name to reference
                this subcommand by. Can optionally be a `list` of names. In this case,
                the first in the list will be treated as the "true" name, and the others
                will be treated as aliases. If no value is provided, `function.__name__` is used
            parsing_method (type[ArgumentParser], optional): The way to parse this command's
                arguments. `ParsingMethod` contains constants to reference for each method.
                Defaults to the parsing method of `self`.
            context (dict[str, Any], optional): Special data that will be
                passed to this command (and any subcommands) at runtime. Defaults to None.
            short_args (dict[str, Union[Iterable[str], str]], optional): Secondary names
                that arguments can be referred to by. Defaults to None.

        Returns:
            Command: the subcommand created
        """

        @self.ensure_function
        def decorator(function: Callable[..., Result]):
            command_name = self.handle_command_aliases(name or function.__name__)
            command = Command(
                command_name,
                function,
                parsing_method or type(self.parser),
                context or {},
                short_args,
            )
            return self.install_command(command)

        return decorator

    def install_commands(self, *commands):
        return tuple(self.install_command(command) for command in commands)

    def install_command(self, command: "Command"):
        """Installs a command object as a subcommand
        of the current object"""
        self.subcommands[command.name] = command
        command.executor.register_callbacks(**self.executor.inheritable_callbacks())

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
