from functools import cached_property
import typing as t
import sys

from arc import errors, utils, logging, typing as at
from arc.color import colorize, fg
from arc.config import config
from arc._command.param import Flag
from arc.autoload import Autoload
from arc._command import helpers, Command
from arc.context import Context
from arc.parser import CLIOptionsParser


logger = logging.getArcLogger("cli")


class CLI(Command):
    """Class for creating multi-command CLI applications


    ## Example
    ```py
    import arc

    cli = arc.CLI()


    @cli.command()
    def c1():
        print("the first command")


    @cli.command()
    def c2():
        print("The second command")


    cli()

    ```
    """

    parser = CLIOptionsParser

    def __init__(
        self,
        name: str = None,
        state: dict = None,
        version: str = None,
        env: at.Env = "production",
        **ctx_dict,
    ):
        """
        Args:
            name: name of the CLI, will be used in the help command. If one is not provided,
                a name will be automatically discovered based on file name.
            state: dictionary of key value pairs to pass to commands
            version: Version string to display with `--version`
            env: Environment of the application. `development` or `production`
            ctx_dict: additional keyword arguments to pass to the execution context
        """

        config.environment = env
        self.version = version
        logging.root_setup(env)
        utils.header("INIT")

        super().__init__(
            lambda: ...,
            name or utils.discover_name(),
            state,
            **ctx_dict,
        )

        if env == "development":
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
                Flag(
                    "version",
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
        kwargs = self.ctx_dict | kwargs
        kwargs["execute_callbacks"] = False

        utils.header("CLI")
        with self.create_ctx(fullname or self.name, **kwargs) as ctx:
            try:
                args = self.get_args(args)
                self.parse_args(ctx, args, allow_extra=True)
                self.execute(ctx)
                args = t.cast(list[str], ctx.extra)

                if not args:
                    logger.debug("No arguments present")
                    print(self.get_usage(ctx))
                    return

                subcommand_name = args.pop(0)
                command_namespace = helpers.get_command_namespace(subcommand_name)
                if not command_namespace:
                    raise errors.CommandNotFound("No command name provided", ctx)

                logger.debug("Executing subcommand: %s", subcommand_name)

                try:
                    command_chain = helpers.find_command_chain(
                        self, command_namespace, ctx
                    )
                except errors.CommandNotFound as e:
                    if config.environment == "development":
                        raise

                    print(str(e))
                    raise errors.Exit(1)

                return command_chain[-1].main(
                    args,
                    subcommand_name,
                    parent=ctx,
                    command_chain=command_chain,
                )

            except errors.Exit as e:
                sys.exit(e.code)

    def command(self, *args, **kwargs):
        """Alias for `Command.subcommand`

        Returns:
            Command: The subcommand's command object
        """
        return self.subcommand(*args, **kwargs)

    def options(self, callback: t.Callable) -> Command:
        self._callback = callback
        # In certain circumstances, params
        # may have already been consructed
        # we can del them to cause them to
        # rebuild
        try:
            del self.params
        except AttributeError:
            ...

        if config.environment == "development":
            self.params
            if len(self.pos_params) > 0:
                raise errors.ArgumentError(
                    f"{colorize('@cli.options', fg.YELLOW)} does not allow Argument parameters. "
                    "All arguments must be Option or Flag parameters"
                )

        return self

    def schema(self):
        return {
            "name": self.name,
            "version": self.version,
            "subcommands": {
                name: command.schema() for name, command in self.subcommands.items()
            },
        }

    # def autocomplete(self, completions_for: str = None):
    #     """Enables autocompletion support for this CLI

    #     Args:
    #         completions_for: command for the shell to run autocompletions against.
    #             This will default the name of the CLI, which should generally be the name of
    #             the executable being built. It's useful to set this during testing, if you're
    #             not actually installing a binary locally in development
    #     """
    #     # pylint: disable=import-outside-toplevel
    #     from .autocomplete import autocomplete

    #     autocomplete.state["cli"] = self
    #     autocomplete.state["init"] = {"completions_for": completions_for or self.name}
    #     self.install_command(autocomplete)

    @utils.timer("Autoloading")
    def autoload(self, *paths: str):
        """Attempts to autoload command objects
        into the CLI from the provided paths"""
        Autoload(paths, self).load()
