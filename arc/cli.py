import typing as t
import sys
import os

from arc import errors, utils, logging

from arc.autoload import Autoload
from arc import logging
from arc._command import helpers, Command
from arc.config import config as config_obj


logger = logging.getArcLogger("cli")


class CLI(Command):
    """Core class for arc"""

    def __init__(
        self,
        name: str = None,
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
            lambda: ...,
            name or utils.discover_name(),
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

    @utils.timer("Running")
    def main(
        self,
        args: t.Union[str, list[str]] = None,
        fullname: str = None,
        **kwargs,
    ):
        utils.header("CLI")
        try:
            with self.create_ctx(fullname or self.name, **kwargs) as ctx:
                args = t.cast(list[str], self.get_args(args))
                if not args:
                    logger.debug("No arguments present")
                    print(self.get_usage(ctx))
                    return

                subcommand_name = args.pop(0)
                command_namespace = helpers.get_command_namespace(subcommand_name)
                if not command_namespace:
                    logger.debug("%s is not a valid command namespace", subcommand_name)
                    args.append(subcommand_name)
                    return super().main(args)

                logger.debug("Execution subcommand: %s", subcommand_name)
                try:
                    command_chain = helpers.find_command_chain(self, command_namespace)
                except errors.CommandNotFound as e:
                    print(str(e))
                    raise errors.Exit(1)

                return command_chain[-1](args, subcommand_name, parent=ctx)

        except errors.Exit as e:
            if config_obj.mode == "development":
                raise
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
