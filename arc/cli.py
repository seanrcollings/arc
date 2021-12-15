import typing as t
import sys

from arc import errors, utils

from arc.autoload import Autoload
from arc.parser import Parsed
from arc import logging
from arc.command import helpers

from arc.command import Command
from arc.types import Param, VarKeyword
from arc.config import config as config_obj
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
            lambda: ...,
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

    def main(
        self,
        args: t.Union[str, list[str]] = None,
        fullname: str = None,
        **kwargs,
    ):
        try:
            with self.create_ctx(fullname or self.name, **kwargs) as ctx:
                args = t.cast(list[str], self.get_args(args))
                if not args:
                    print(self.get_usage(ctx))
                    return

                subcommand_name = args.pop(0)
                command_namespace = helpers.get_command_namespace(subcommand_name)
                if not command_namespace:
                    args.append(subcommand_name)
                    return super().main(args)

                command_chain = helpers.find_command_chain(self, command_namespace)
                return command_chain[-1](args, subcommand_name, parent=ctx)
        except errors.Exit as e:
            sys.exit(e.code)

    def command(self, *args, **kwargs):
        """Alias for `Command.subcommand`

        Returns:
            Command: The subcommand's command object
        """
        return self.subcommand(*args, **kwargs)

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
