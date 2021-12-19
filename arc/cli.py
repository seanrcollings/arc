from functools import cached_property
import typing as t
import sys

from arc import errors, utils, logging
from arc._command.param import FlagParam
from arc.autoload import Autoload
from arc._command import helpers, Command
from arc.config import config as config_obj
from arc.context import Context


logger = logging.getArcLogger("cli")


class CLI(Command):
    """Core class for arc"""

    def __init__(
        self,
        name: str = None,
        config: dict[str, t.Any] = None,
        config_file: str = None,
        state: dict = None,
        version: str = None,
        **ctx_dict,
    ):
        """
        Args:
            name: name of the CLI, will be used in the help command.
            config: dictonary of configuration values
            config_file: filename to load configuration information from
            state: dictionary of key value pairs to pass to commands
            version: Version string to display with `--version`
            ctx_dict: additional keyword arguments to pass to the execution
            context
        """

        self.version = version

        super().__init__(
            lambda: print("CLI stub function."),
            name or utils.discover_name(),
            state,
            **ctx_dict,
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

    @cached_property
    def params(self):
        params = super().params
        if self.version:

            def _version_callback(value, ctx: Context, _param):
                if value:
                    print(self.version)
                    ctx.exit()

            params.append(
                FlagParam(
                    "version",
                    bool,
                    short="v",
                    description="Displays the app's current version",
                    callback=_version_callback,
                )
            )

        return params

    @utils.timer("Running CLI")
    def main(
        self,
        args: t.Union[str, list[str]] = None,
        fullname: str = None,
        **kwargs,
    ):
        utils.header("CLI")
        try:
            with self.create_ctx(
                fullname or self.name, **(self.ctx_dict | kwargs)
            ) as ctx:
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

                logger.debug("Executing subcommand: %s", subcommand_name)
                try:
                    command_chain = helpers.find_command_chain(self, command_namespace)
                except errors.CommandNotFound as e:
                    print(str(e))
                    raise errors.Exit(1)

                return command_chain[-1].main(
                    args,
                    subcommand_name,
                    parent=ctx,
                    command_chain=command_chain,
                )

        except errors.Exit as e:
            if config_obj.mode == "development" and e.code != 0:
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

        autocomplete.state["cli"] = self
        autocomplete.state["init"] = {"completions_for": completions_for or self.name}
        self.install_command(autocomplete)

    @utils.timer("Autoloading")
    def autoload(self, *paths: str):
        """Attempts to autoload command objects
        into the CLI from the provided paths"""
        Autoload(paths, self).load()
