from __future__ import annotations
import collections
import typing as t
import abc
import sys
from importlib import import_module, metadata
from pathlib import Path


if t.TYPE_CHECKING:
    from arc.runtime import Context

Plugin = t.Callable[["Context"], None]


class PluginManager(collections.UserDict[str, Plugin]):
    def register(self, name: str, plugin: Plugin) -> None:
        self[name] = plugin

    def unregister(self, name: str) -> None:
        del self[name]

    def paths(self, *locations: str) -> None:
        loader = PathPluginLoader(self, locations)
        loader.load()

    def groups(self, *locations: str) -> None:
        loader = EntryPointsPluginLoader(self, locations, "group")
        loader.load()

    def entrypoints(self, *locations: str) -> None:
        loader = EntryPointsPluginLoader(self, locations, "value")
        loader.load()


class PluginLoader(abc.ABC):
    def __init__(self, manager: PluginManager, locations: t.Iterable[str]) -> None:
        self.manager = manager
        self.locations = locations

    @abc.abstractmethod
    def load(self) -> None:
        ...


class EntryPointsPluginLoader(PluginLoader):
    """Loads plugins from entry point groups

    https://packaging.python.org/en/latest/specifications/entry-points/
    """

    def __init__(
        self,
        manager: PluginManager,
        locations: t.Iterable[str],
        filter: str,
    ) -> None:
        self.filter = filter
        super().__init__(manager, locations)

    def load(self) -> None:
        for entry_point in self.__get_entry_points(self.locations):
            plugin = entry_point.load()
            self.manager.register(entry_point.name, plugin)

    def __get_entry_points(
        self, locations: t.Iterable[str]
    ) -> t.Iterator[metadata.EntryPoint]:
        for location in locations:
            for entry_point in metadata.entry_points(**{self.filter: location}):
                yield entry_point  # type: ignore


class PathPluginLoader(PluginLoader):
    """Loads plugins from a a set of file paths"""

    def load(self) -> None:
        for path in self.__get_paths(self.locations):
            plugin = self.__load_plugin(path)

            if plugin:
                self.manager.register(str(path), plugin)

    def __get_paths(self, paths: t.Iterable[str]) -> t.Iterator[Path]:
        for filepath in paths:
            path = self.path(filepath)
            if not path:
                continue

            if path.name.startswith("__"):
                continue

            if path.is_dir():
                yield from self.__get_paths(path.iterdir())  # type: ignore
            else:
                yield path

    def __load_plugin(self, path: Path) -> Plugin | None:
        sys.path.append(str(path.parent))
        module = import_module(path.stem)
        return getattr(module, "plugin", None)

    @staticmethod
    def path(filepath: str) -> t.Optional[Path]:
        path = Path(filepath)
        path = path.expanduser().resolve()
        if path.exists():
            return path
        return None
