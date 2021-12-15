import typing as t

from arc import utils

from arc.autoload import Autoload
from arc.parser import Parsed
from arc import logging

from arc.command import Command
from arc.present.help_formatter import print_help
from arc.types import Context, Param, VarKeyword
from arc.config import config as config_obj
from arc.execution_state import ExecutionState
from arc.types.var_types import VarPositional


class CLI(Command):
    """Core class for arc"""

    def __init__(
        self,
        name: str = "cli",
        config: dict[str, t.Any] = None,
        config_file: str = None,
        context: dict = None,
        version: str = "¯\\_(ツ)_/¯",
    ):
        """Creates a CLI object.
        Args:
            name: name of the CLI, will be used in the help command.
            arcfile: arc config file to load. defaults to ./.arc
            context: dictionary of key value pairs to pass to children as context
            version: Version string to display with `--version`
        """

        super().__init__(
            name,
            lambda: print("default behavior"),
            context,
        )

        if config:
            config_obj.set_values(config)
        if config_file:
            config_obj.from_file(config_file)

        logging.root_setup()
        utils.header("INIT")

        if config_obj.mode == "development":
            from ._debug import debug  # pylint: disable=import-outside-toplevel

            self.install_command(debug)

        self.version = version
        # self.install_command(Command("help", self.helper))

    def main(self, args: t.Union[str, list[str]] = None):
        args = t.cast(list[str], self.get_args(args))
        subcommand_name = args.pop(0)

    def command(self, *args, **kwargs):
        """Alias for `Command.subcommand`

        Returns:
            Command: The subcommand's command object
        """
        return self.subcommand(*args, **kwargs)

    def missing_command(
        self,
        ctx: Context,
        _help: bool = Param(name="help", short="h", description="display this help"),
        version: bool = Param(short="v", description="display application version "),
    ):
        """View specific help with "help <command-name>" """
        if _help:
            return self("help")
        elif version:
            print(self.name, self.version)
            return

        return self("help")

    # def helper(
    #     self,
    #     command_name: str = "",
    # ):
    #     """Displays information for a given command
    #     By default, shows help for the top-level command.
    #     To see a specific command's information, provide
    #     a command name (some:command:name)
    #     """
    #     parsed: Parsed = {"pos_values": [command_name], "key_values": {}}
    #     namespace = get_command_namespace(parsed)
    #     chain = find_command_chain(self, namespace)
    #     state = ExecutionState(
    #         user_input=[],
    #         command_namespace=namespace,
    #         command_chain=chain,
    #         parsed=parsed,
    #     )
    #     print_help(state.command, state)

    def schema(self):
        return {
            "name": self.name,
            "version": self.version,
            "subcommands": {
                name: command.schema() for name, command in self.subcommands.items()
            },
        }

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
