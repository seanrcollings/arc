from typing import Iterable, Optional, Generator
from importlib import import_module
from pathlib import Path
import logging
import sys

from arc.command import Command
from arc.color import fg, effects
from arc.errors import CommandError

logger = logging.getLogger("arc_logger")


class Autoload:
    def __init__(self, paths: Iterable[str], parent: Command):
        self.paths = paths
        self.parent = parent

    def load(self):
        for path in self.__load_files(self.paths):
            logger.debug("Autoloading %s%s%s", fg.YELLOW, path, effects.CLEAR)
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
