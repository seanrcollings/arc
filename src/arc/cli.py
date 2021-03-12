import sys
from typing import List, Union, Optional, Iterable, Generator
from importlib import import_module
from pathlib import Path

from arc.parser import parse
from arc import arc_config, utils

from .color import effects, fg
from .command import KeywordCommand, Command
from .errors import CommandError


class CLI(KeywordCommand):
    """The CLI class is now implemented as a subclass
    of the Command class and reality just acts as a
    conveneince wrapper around Command creation and
    the run function.
    """

    def __init__(self, name="cli", function=utils.no_op, arcfile=".arc", context=None):
        """Creates a CLI object.

        :param name: name of the CLI, will be used in the help command
        :param arcfile: arc config file to load. defaults to ./.arc
        :param context: dict of key value pairs to pass to children as context"""

        super().__init__(name, function, context)
        arc_config.from_file(arcfile)

    # pylint: disable=arguments-differ
    def __call__(self, execute: Optional[str] = None):  # type: ignore
        return run(self, execute)

    def command(self, *args, **kwargs):
        return self.subcommand(*args, **kwargs)

    # Need to stub these in
    # because Command is abstract,
    # but they shouldn't every be called
    # (at least right now: https://github.com/seanrcollings/arc/issues/63)
    def execute(self, _):
        ...

    def match_input(self, _):
        ...

    @utils.timer("Autoloading")
    def autoload(self, *paths: str):
        Autoload(paths, self).load()

    def helper(self, level: int = 0):
        """Displays this help.
        """
        print(f"Usage: {self.name} <COMMAND> [ARGUMENTS ...]\n\n")
        print(f"{effects.UNDERLINE}{effects.BOLD}Commands:{effects.CLEAR}\n")
        for command in self.subcommands.values():
            command.helper(level)


class Autoload:
    def __init__(self, paths: Iterable[str], parent: Command):
        self.paths = paths
        self.parent = parent

    def load(self):
        for path in self.__load_files(self.paths):
            utils.logger.debug("Autoloading %s%s%s", fg.YELLOW, path, effects.CLEAR)
            for command in self.__load_commands(path):
                if command.name in self.parent.subcommands:
                    raise CommandError(
                        f"Namespace {command.name} already exists on {self.parent}\n"
                        "Autoloaded namespaces cannot overwrite prexisting namespaces"
                    )

                self.parent.install_command(command)

    def __load_files(self, paths: Iterable[str]):
        for filepath in paths:
            path = self.path(filepath)
            if not path:
                continue

            if path.name.startswith("__"):
                continue

            if path.is_dir():
                yield from self.__load_files(path.iterdir())  # type: ignore
            else:
                yield path

    def __load_commands(self, path: Path) -> Generator[Command, None, None]:
        sys.path.append(str(path.parent))
        module = import_module(path.stem)
        module_objects = (
            getattr(module, name) for name in dir(module) if not name.startswith("__")
        )
        for obj in module_objects:
            if isinstance(obj, type):
                continue

            try:
                if Command in obj.__class__.mro() and obj.__autoload__:
                    yield obj
            except AttributeError:
                continue

    @staticmethod
    def path(filepath: str) -> Optional[Path]:
        path = Path(filepath)
        path = path.expanduser().resolve()
        if path.exists():
            return path
        return None


def run(
    command: Command, execute: Optional[str] = None, arcfile: Optional[str] = None,
):
    """Core function of the ARC API.
    Loads up the config file, parses the user input
    And then passes control over to the `command` object.

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
    with utils.handle(CommandError):
        return command.run(command_node)
