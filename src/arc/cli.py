import sys
from typing import List, Union, Optional, Callable

from arc.parser import parse
from arc import arc_config, utils
from .color import effects, fg
from .command import KeywordCommand, Command
from .errors import CommandError
from .autoload import Autoload


class CLI(KeywordCommand):
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

        super().__init__(name, self.__default, context)
        arc_config.from_file(arcfile)
        self.version = version
        self.add_helper()
        self.default_action: Optional[Command] = self.base()(
            function
        ) if function else self.subcommands["help"]

    # pylint: disable=arguments-differ
    def __call__(self, execute: str = None):  # type: ignore
        return run(self, execute)

    def command(self, *args, **kwargs):
        return self.subcommand(*args, **kwargs)

    def base(self, name=None, command_type=None, **kwargs):
        """Define The CLI's default behavior
        when not given a specific command. Has the same interface
        as `Command.subcommand`
        """

        @self.ensure_function
        def decorator(function):
            command_name = name or function.__name__
            self.default_action = self.create_command(
                command_name, function, command_type, **kwargs
            )

            self.args |= self.default_action.args
            return self.default_action

        return decorator

    def __default(self, help: bool, version: bool, **kwargs):
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

    def helper(self, level: int = 0):
        """Displays this help."""
        print(f"Usage: {self.name} <COMMAND> [ARGUMENTS ...]\n\n")
        print(f"{effects.UNDERLINE}{effects.BOLD}Commands:{effects.CLEAR}\n")
        for command in self.subcommands.values():
            command.helper(level)


def run(
    command: Command, execute: Optional[str] = None, arcfile: Optional[str] = None,
):
    """Core function of the ARC API.
    Loads up the config file, parses the user input
    Finds the command referenced, then passes over control to it

    :param command: command object to run
    :param execute: string to parse and execute. If it's not provided
        sys.argv will be used
    :param arcfile: file path to an arc config file to load,
        will ignore if path does not exsit
    """
    if arcfile:
        arc_config.from_file(arcfile)

    user_input: Union[List[str], str] = execute if execute else sys.argv[1:]
    command_node = parse(user_input)
    utils.logger.debug(command_node)

    current_namespace: list[str] = []
    subcommand_name = command.name
    with utils.handle(CommandError):
        while not command_node.empty_namespace():
            subcommand_name = command_node.namespace.pop(0)
            current_namespace.append(subcommand_name)

            if subcommand_name not in command.subcommands:
                raise CommandError(
                    f"The command {fg.YELLOW}"
                    f"{':'.join(current_namespace)}{effects.CLEAR}{fg.RED} not found. "
                    "Check --help for available commands"
                )

            command = command.subcommands[subcommand_name]

        return command.run(command_node)
