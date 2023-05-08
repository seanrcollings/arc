from __future__ import annotations

import sys
import typing as t
from importlib import import_module
from pathlib import Path

from arc.errors import CommandError

if t.TYPE_CHECKING:
    from arc.define import Command


class Autoload:
    """Autoloads commands from files and adds them to the parent command"""

    def __init__(
        self, paths: t.Iterable[str], parent: Command, allow_overrite: bool = False
    ) -> None:
        self.paths = paths
        self.parent = parent
        self.allow_overwrite = allow_overrite

    def load(self) -> None:
        for path in self.__load_files(self.paths):
            for command in self.__load_commands(path):
                if command.name in self.parent.subcommands and not self.allow_overwrite:
                    raise CommandError(
                        f"Command {command.name} already exists on {self.parent}\n"
                        "Autoloaded command cannot overwrite prexisting commands"
                    )
                self.parent.add_command(command)

    def __load_files(self, paths: t.Iterable[str]) -> t.Iterator[Path]:
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

    def __load_commands(self, path: Path) -> t.Generator[Command, None, None]:
        sys.path.append(str(path.parent))
        module = import_module(path.stem)
        module_objects = (
            getattr(module, name) for name in dir(module) if not name.startswith("__")
        )
        for obj in module_objects:
            if isinstance(obj, type):
                continue

            try:
                if obj._autoload:
                    yield obj
            except AttributeError:
                continue

    @staticmethod
    def path(filepath: str) -> t.Optional[Path]:
        path = Path(filepath)
        path = path.expanduser().resolve()
        if path.exists():
            return path
        return None
