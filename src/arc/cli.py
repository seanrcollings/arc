import sys
from typing import List, Union, Optional, Callable, Any
import textwrap
import shlex

from arc import arc_config, utils
from .color import effects, fg
from .command import Command, ParsingMethod
from .errors import CommandError
from .autoload import Autoload


class CLI(Command):
    """The CLI class is now implemented as a subclass
    of the Command class and reality just acts as a
    conveneince wrapper around Command creation and
    the run function.
    """

    def __init__(
        self,
        name: str = "cli",
        function: Callable = None,
        arcfile: str = ".arc",
        context: dict = None,
        version: str = "¯\\_(ツ)_/¯",
    ):
        """Creates a CLI object.

        :param name: name of the CLI, will be used in the help command
        :param function: function that defines the CLI's default behavior. Identical
            to calling `@cli.base()`
        :param arcfile: arc config file to load. defaults to ./.arc
        :param context: dictionary of key value pairs to pass to children as context
        :param version: Version string to display with `--version`
        """

        super().__init__(name, self.missing_command, ParsingMethod.KEYWORD, context)
        arc_config.from_file(arcfile)
        self.version = version
        # self.install_command(self.create_command("help", self.helper))
        # self.default_action: Optional[Command] = self.base()(
        #     function
        # ) if function else self.subcommands["help"]

    # pylint: disable=arguments-differ
    def __call__(self, execute: str = None):  # type: ignore
        return run(self, execute)

    def command(self, *args, **kwargs):
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
        the `@cli.base()` definition
        """
        if help:
            self("help")
        elif version:
            print(self.name, self.version)
        elif self.default_action:
            self.default_action(**kwargs)

    def autocomplete(self, completions_for: str = None, completions_from: str = None):
        """Enables autocompletion support for this CLI

        :param str completions_for: command for the shell to run autocompletions against.
        This will defautl the name of the CLI, which should generally be the name of
        the executable being built. It's useful to set this during testing, if you're
        not actually installing a binary locally in development

        :param str completions_from: command for the shell to run to generate the
        autocompletions
        """
        # pylint: disable=import-outside-toplevel
        from .autocomplete import autocomplete

        autocomplete.context["cli"] = self
        autocomplete.context["init"] = {
            "completions_for": completions_for or self.name,
            "completions_from": completions_from or self.name,
        }
        self.install_command(autocomplete)

    @utils.timer("Autoloading")
    def autoload(self, *paths: str):
        Autoload(paths, self).load()

    def helper(self):
        """Displays this help."""
        print(f"Usage: {self.name} <COMMAND> [ARGUMENTS ...]\n\n")
        print(f"{effects.UNDERLINE}{effects.BOLD}Commands:{effects.CLEAR}\n")
        for command in self.subcommands.values():
            display_help(command, self)


def display_help(command: Command, parent: Command, level: int = 0):
    sep = arc_config.namespace_sep
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


# TODO: Get missing_command working
def run(
    command: Command, execute: Optional[str] = None, arcfile: Optional[str] = None,
):
    """Core function of the ARC API.
    Loads up the config file, parses the user input
    Finds the command referenced, then passes over control to it

    :param command: command object to run
    :param execute: string to parse and execute. If it's not provided
        `sys.argv` will be used
    :param arcfile: file path to an arc config file to load,
        will ignore if path does not exsit
    """
    if arcfile:
        arc_config.from_file(arcfile)

    user_input: Union[List[str], str] = execute if execute else sys.argv[1:]
    if isinstance(user_input, str):
        user_input = shlex.split(user_input)

    # How do we know if the command namespace is empty?
    command_namespace: list[str] = user_input[0].split(arc_config.namespace_sep)
    command_args: list[str] = user_input[1:]
    command_ctx: dict[str, Any] = command.context

    with utils.handle(CommandError):
        for subcommand_name in command_namespace:
            if subcommand_name in command.subcommands:
                command = command.subcommands[subcommand_name]
            elif subcommand_name in command.subcommand_aliases:
                command = command.subcommands[
                    command.subcommand_aliases[subcommand_name]
                ]
            else:
                raise CommandError(
                    f"The command {fg.YELLOW}"
                    f"{':'.join(command_namespace)}{effects.CLEAR}{fg.RED} not found. "
                    "Check --help for available commands"
                )

            command_ctx = command.context | command_ctx

        utils.logger.debug(
            "Executing command: %s%s%s",
            fg.YELLOW,
            ":".join(command_namespace),
            effects.CLEAR,
        )
        return command.run(command_namespace, command_args, command_ctx)
