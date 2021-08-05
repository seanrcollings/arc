import logging
from typing import Callable, Optional, Type

from arc import help_text, utils
from arc.autoload import Autoload
from arc.color import effects, fg
from arc.command import (
    ArgumentParser,
    Command,
    ParsingMethod,
    PositionalParser,
    Context,
)
from arc.config import config
from arc.run import find_command_chain, run


class CLI(Command):
    """Core class for arc"""

    def __init__(
        self,
        name: str = "cli",
        function: Callable = None,
        parsing_method: Type[ArgumentParser] = ParsingMethod.STANDARD,
        arcfile: str = ".arc",
        context: dict = None,
        version: str = "¯\\_(ツ)_/¯",
    ):
        """Creates a CLI object.
        Args:
            name: name of the CLI, will be used in the help command.
            function: function that defines the CLI's default behavior.
                Identical to calling `@cli.default()`.
            arcfile: arc config file to load. defaults to ./.arc
            context: dictionary of key value pairs to pass to children as context
            version: Version string to display with `--version`
        """

        super().__init__(
            name,
            self.missing_command,
            parsing_method,
            context,
            short_args={"help": "h", "version": "v"},
        )
        config.from_file(arcfile)
        self.__logging_setup()
        utils.header("INIT")
        self.version = version
        self.install_command(Command("help", self.helper, parser=PositionalParser))
        self.default_action: Optional[Command] = (
            self.default()(function) if function else None
        )

    # pylint: disable=arguments-differ
    def __call__(  # type: ignore
        self,
        execute: str = None,
        handle_exception: bool = True,
        check_result: bool = True,
    ):
        return run(
            self,
            execute,
            handle_exception=handle_exception,
            check_result=check_result,
        )

    def command(self, *args, **kwargs):
        """Alias for `Command.subcommand`

        Returns:
            Command: The subcommand's command object
        """
        return self.subcommand(*args, **kwargs)

    def default(self, name=None, parse_method=None, **kwargs):
        """Define The CLI's default behavior
        when not given a specific command. Has the same interface
        as `Command.subcommand`
        """

        @self.ensure_function
        def decorator(function):
            self.default_action = Command(
                name or function.__name__,
                function,
                parse_method or type(self.parser),
                **kwargs,
            )

            return self.default_action

        return decorator

    # pylint: disable=redefined-builtin
    def missing_command(self, help: bool, version: bool, ctx: Context, **_kwargs):
        """Handles default arguments
        View specific help with "help <command-name>"

        # Arguments
            help: shows this help
            version: displays the version
        """
        if help:
            return self("help")
        elif version:
            print(self.name, self.version)
        elif self.default_action:
            if self.default_action:
                ctx.execution_state.command = self.default_action
                return self.default_action.run(ctx.execution_state)

            return self("help")

    def autocomplete(self, completions_for: str = None):
        """Enables autocompletion support for this CLI

        Args:
            completions_for: command for the shell to run autocompletions against.
                This will default the name of the CLI, which should generally be the name of
                the executable being built. It's useful to set this during testing, if you're
                not actually installing a binary locally in development
        """
        # pylint: disable=import-outside-toplevel
        from .autocomplete import autocomplete

        autocomplete.context["cli"] = self
        autocomplete.context["init"] = {"completions_for": completions_for or self.name}
        self.install_command(autocomplete)

    @utils.timer("Autoloading")
    def autoload(self, *paths: str):
        """Attempts to autoload command objects
        into the CLI from the provided paths"""
        Autoload(paths, self).load()

    def helper(self, command_name: str = ""):
        """Displays information for a given command
        By default, shows help for the top-level command.
        To see a specific command's information, provide
        a command name (some:command:name)
        """
        namespace = command_name.split(config.namespace_sep) if command_name else []
        help_text.display_help(
            self,
            find_command_chain(self, namespace)[-1],
            namespace,
        )

    def __logging_setup(self):
        root = logging.getLogger("arc_logger")
        level = config.mode_map.get(config.mode, logging.WARNING)
        root.setLevel(level)
        handler = logging.StreamHandler()
        formatter = ArcFormatter()
        handler.setFormatter(formatter)
        root.addHandler(handler)


class ArcFormatter(logging.Formatter):
    prefixes = {
        logging.INFO: f"{fg.BLUE}🛈{effects.CLEAR} ",
        logging.WARNING: f"{fg.YELLOW}{effects.BOLD}WARNING{effects.CLEAR}: ",
        logging.ERROR: f"{fg.RED}{effects.BOLD}ERROR{effects.CLEAR}: ",
    }

    def format(self, record: logging.LogRecord):
        prefix = self.prefixes.get(record.levelno, "")
        record.msg = prefix + str(record.msg)
        return super().format(record)
