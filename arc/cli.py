import logging
from typing import Annotated, Callable, Optional, Any

from arc import utils
from arc.autoload import Autoload

from arc.types.params import Meta, VarKeyword
from arc.command import Command, Context
from arc.config import config as config_obj
from arc.run import find_command_chain, get_command_namespace, run
from arc.execution_state import ExecutionState


class CLI(Command):
    """Core class for arc"""

    def __init__(
        self,
        name: str = "cli",
        function: Callable = None,
        config: dict[str, Any] = None,
        config_file: str = None,
        context: dict = None,
        version: str = "¯\\_(ツ)_/¯",
    ):
        """Creates a CLI object.
        Args:
            name: name of the CLI, will be used in the help command.
            function: function that defines the CLI's default behavior.
                Identical to calling `@cli.default()`.
            arcfile: arc config file to load. defaults to ./.arc
            context: dictionary of key value pairs to pass to children as context
            version: Version string to display with `--version`
        """

        super().__init__(
            name,
            self.missing_command,
            context,
        )

        if config:
            config_obj.set_values(config)
        if config_file:
            config_obj.from_file(config_file)

        self.__logging_setup()
        utils.header("INIT")
        self.version = version
        self.install_command(Command("help", self.helper))
        self.default_action: Optional[Command] = (
            self.default()(function) if function else None
        )

    # pylint: disable=arguments-differ
    def __call__(  # type: ignore
        self,
        execute: str = None,
        handle_exception: bool = True,
        check_result: bool = True,
    ):
        return run(
            self,
            execute,
            handle_exception=handle_exception,
            check_result=check_result,
        )

    def command(self, *args, **kwargs):
        """Alias for `Command.subcommand`

        Returns:
            Command: The subcommand's command object
        """
        return self.subcommand(*args, **kwargs)

    def default(self, name=None, **kwargs):
        """Define The CLI's default behavior
        when not given a specific command. Has the same interface
        as `Command.subcommand`
        """

        def decorator(wrapped):
            if isinstance(wrapped, Command):
                wrapped = wrapped.executable.wrapped

            self.default_action = Command(
                name or wrapped.__name__,
                wrapped,
                **kwargs,
            )

            return self.default_action

        return decorator

    # pylint: disable=redefined-builtin
    def missing_command(
        self,
        _help: Annotated[bool, Meta(name="help", short="h")],
        version: Annotated[bool, Meta(short="v")],
        ctx: Context,
        kwargs: VarKeyword,
    ):
        """View specific help with "help <command-name>"

        # Arguments
            help: shows this help
            version: displays the version
        """
        if _help:
            return self("help")
        elif version:
            print(self.name, self.version)
            return
        elif self.default_action:
            ctx.state.command_chain += [self.default_action]
            return self.default_action.run(ctx.state)

        return self("help")

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

    def helper(self, command_name: Annotated[str, Meta(default="")]):
        """Displays information for a given command
        By default, shows help for the top-level command.
        To see a specific command's information, provide
        a command name (some:command:name)
        """
        namespace, _args = get_command_namespace([command_name])
        chain = find_command_chain(self, namespace)
        state = ExecutionState(
            user_input=[],
            command_namespace=namespace,
            command_args=[],
            command_chain=chain,
        )
        print(state.command.doc(state))

    def __logging_setup(self):
        root = logging.getLogger("arc_logger")
        if len(root.handlers) == 0:
            level = config_obj.mode_map.get(config_obj.mode, logging.WARNING)
            root.setLevel(level)
            handler = logging.StreamHandler()
            formatter = ArcFormatter()
            handler.setFormatter(formatter)
            root.addHandler(handler)


class ArcFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        from arc.color import colorize, effects, fg

        prefixes = {
            logging.INFO: colorize("🛈 ", fg.BLUE),
            logging.WARNING: colorize("WARNING", fg.YELLOW, effects.BOLD) + ": ",
            logging.ERROR: colorize("ERROR", fg.RED, effects.BOLD) + ": ",
        }

        prefix = prefixes.get(record.levelno, "")
        record.msg = prefix + str(record.msg)
        return super().format(record)
