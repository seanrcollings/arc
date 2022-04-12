from functools import cached_property
import typing as t
import sys

from arc import constants, errors, utils, logging
from arc.autocompletions import Completion, CompletionInfo, get_completions
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
        **ctx_dict,
    ):
        """
        Args:
            name: name of the CLI, will be used in the help command. If one is not provided,
                a name will be automatically discovered based on file name.
            state: dictionary of key value pairs to pass to commands
            ctx_dict: additional keyword arguments to pass to the execution context
        """
        utils.header("INIT")

        super().__init__(
            lambda: ...,
            name or utils.discover_name(),
            state,
            **ctx_dict,
        )

    def __completions__(self, info: CompletionInfo, *_args, **_kwargs):
        # Completes Command names
        if (
            (len(info.words) == 0 and info.current == "")
            or (len(info.words) == 1 and info.current == info.words[-1])
        ) and not info.current.startswith(constants.SHORT_FLAG_PREFIX):
            return [
                Completion(fullname, description=command.short_description or "")
                for command, fullname in helpers.get_all_commands(self)[1:]
            ]
        # Finds the current command and delegates completions to it
        elif len(info.words) >= 1:
            command_name = info.words[0]
            for command, fullname in helpers.get_all_commands(self):
                if fullname == command_name:
                    return get_completions(command, info)

        return []
        # Completes Global Options
        # return super().__completions__(info)

    @utils.timer("Running CLI")
    def _main(
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
                    raise errors.Exit(1)

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

                return command_chain[-1]._main(  # pylint: disable=protected-access
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

    @utils.timer("Autoloading")
    def autoload(self, *paths: str):
        """Attempts to autoload command objects
        into the CLI from the provided paths"""
        Autoload(paths, self).load()
