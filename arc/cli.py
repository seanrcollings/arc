from typing import Optional, Callable, Type
import logging

from arc import utils, help_text
from arc.config import config
from .color import effects, fg
from .command import Command, ParsingMethod, ArgumentParser, PositionalParser
from .autoload import Autoload
from .run import run, find_command


class CLI(Command):
    """Core class for arc"""

    def __init__(
        self,
        name: str = "cli",
        function: Callable = None,
        parsing_method: Type[ArgumentParser] = ParsingMethod.KEYWORD,
        arcfile: str = ".arc",
        context: dict = None,
        version: str = "¯\\_(ツ)_/¯",
    ):
        """Creates a CLI object.
        Args:
            name: name of the CLI, will be used in the help command.
            function: function that defines the CLI's default behavior.
                Identical to calling `@cli.base()`.
            arcfile: arc config file to load. defaults to ./.arc
            context: dictionary of key value pairs to pass to children as context
            version: Version string to display with `--version`
        """

        super().__init__(name, self.missing_command, parsing_method, context)
        config.from_file(arcfile)
        self.__logging_setup()
        utils.header("INIT")
        self.version = version
        self.install_command(Command("help", self.helper, parser=PositionalParser))
        self.default_action: Optional[Command] = (
            self.base()(function) if function else self.subcommands["help"]
        )

    # pylint: disable=arguments-differ
    def __call__(self, execute: str = None):  # type: ignore
        return run(self, execute)

    def command(self, *args, **kwargs):
        """Alias for `Command.subcommand`

        Returns:
            Command: The subcommand's command object
        """
        return self.subcommand(*args, **kwargs)

    def base(self, name=None, parse_method=None, **kwargs):
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

            self.parser.args |= self.default_action.parser.args
            return self.default_action

        return decorator

    # pylint: disable=redefined-builtin
    def missing_command(self, help: bool, version: bool, **kwargs):
        """Handles default arguments

        # Arguments
            --help     shows this help
            --version  displays the version
        """
        if help:
            self("help")
        elif version:
            print(self.name, self.version)
        elif self.default_action:
            return self.default_action(**kwargs)

    def autocomplete(self, completions_for: str = None, completions_from: str = None):
        """Enables autocompletion support for this CLI

        **Currently disabled**

        Args:
            completions_for: command for the shell to run autocompletions against.
                This will default the name of the CLI, which should generally be the name of
                the executable being built. It's useful to set this during testing, if you're
                not actually installing a binary locally in development
            completions_from: command for the shell to run to generate the
                autocompletions
        Raises:
            NotImplementedError
        """
        raise NotImplementedError("Autocompletion disabled until further notice")
        # pylint: disable=import-outside-toplevel
        # from .autocomplete import autocomplete

        # autocomplete.context["cli"] = self
        # autocomplete.context["init"] = {
        #     "completions_for": completions_for or self.name,
        #     "completions_from": completions_from or self.name,
        # }
        # self.install_command(autocomplete)

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
            find_command(self, namespace)[0],
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
