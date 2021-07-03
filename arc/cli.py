from typing import Optional, Callable, Type
import textwrap

from arc import utils
from arc.config import config
from .color import effects, fg
from .command import Command, ParsingMethod, ArgumentParser
from .autoload import Autoload
from .run import run


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
        utils.header("INIT")
        self.version = version
        self.install_command(Command("help", self.helper))
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
        """When no command is provided,
        this function will be called to handle it.
        It handles the --help and --version flags.
        And if neither of those are specified, it will call
        the default action
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

    def helper(self):
        """Displays the help"""
        print(f"Usage: {self.name} <COMMAND> [ARGUMENTS ...]\n\n")
        print(f"{effects.UNDERLINE}{effects.BOLD}Commands:{effects.CLEAR}\n")
        for command in self.subcommands.values():
            display_help(command, self)


def display_help(command: Command, parent: Command, level: int = 0):
    """Generates the help documentation for a command.

    Args:
        command (Command): Command that acts as the root of the help documentation
        parent (Command): The command's parent Command
        level (int, optional): Depth of the Command in the Command tree.
            Used to calculate spacing. Defaults to 0.
    """
    sep = config.namespace_sep
    indent = "    " * level

    aliases = [
        key for key, value in parent.subcommand_aliases.items() if value == command.name
    ]
    name = f"{fg.GREEN}{command.name}{effects.CLEAR}"
    if aliases:
        name += f"{fg.BLACK.bright} ({', '.join(aliases)}){effects.CLEAR}"

    info = []

    info.append(
        textwrap.indent(name, indent)
        if level == 0
        else textwrap.indent(sep + name, indent)
    )

    info.append(textwrap.indent(command.doc, indent + "  ") if command.doc else "")

    if len(command.subcommands) > 0:
        info.append(
            textwrap.indent(
                f"{effects.BOLD}{effects.UNDERLINE}Subcomands:{effects.CLEAR}",
                indent + "  ",
            )
        )

    print("\n".join(info))

    for sub in command.subcommands.values():
        display_help(sub, command, level + 1)
