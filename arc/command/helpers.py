from __future__ import annotations
import inspect
from typing import TYPE_CHECKING, get_type_hints, Union, Iterable

from arc import utils, errors
from arc.config import config
from .argument import Argument, EMPTY
from .context import Context

if TYPE_CHECKING:
    from .command import Command


HIDDEN_ARG_TYPES = {Context}


class ParamProxy:
    def __init__(self, param: inspect.Parameter, annotation: type):
        self.param = param
        self.annotation = annotation

    def __getattr__(self, name):
        return getattr(self.param, name)


class ArgBuilder:
    def __init__(self, function, arg_aliases=None):
        self.__annotations = get_type_hints(function)
        self.__sig = inspect.signature(function)
        self.__length = len(self.__sig.parameters.values())
        self.__args: dict[str, Argument] = {}
        self.__arg_aliases: dict[str, Union[Iterable[str], str]] = arg_aliases or {}
        self.__ensure_unique_aliases()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self

    def __len__(self):
        return self.__length

    def __iter__(self):
        for param in self.__sig.parameters.values():
            proxy = ParamProxy(param, self.__annotations.get(param.name, str))
            yield proxy
            self.add_arg(proxy)

    @property
    def args(self):
        return self.__args

    def add_arg(self, param: ParamProxy):
        arg = None
        if param.annotation is bool:
            default = False if param.default is EMPTY else param.default
            arg = Argument(param.name, param.annotation, default)

        elif param.kind not in (param.VAR_KEYWORD, param.VAR_POSITIONAL):
            arg = Argument(
                param.name, param.annotation, param.default, self.is_hidden_arg(param)
            )

        if arg:
            if aliases := self.__arg_aliases.get(arg.name):
                if isinstance(aliases, str):
                    arg.aliases.add(aliases)
                arg.aliases.update(self.__arg_aliases[arg.name])

            self.__args[param.name] = arg

    def is_hidden_arg(self, param: ParamProxy) -> bool:
        annotation = utils.unwrap_type(param.annotation)

        try:
            for kind in HIDDEN_ARG_TYPES:
                if annotation is kind or issubclass(annotation, kind):
                    return True
        except TypeError:
            return False

        return False

    def get_meta(self, **kwargs):
        return dict(length=self.__length, **kwargs)

    def __ensure_unique_aliases(self):
        aliases = []
        for alias in self.__arg_aliases.values():
            if isinstance(alias, str):
                aliases.append(alias)
            else:
                aliases += list(alias)

        if len(set(aliases)) != len(aliases):
            raise errors.CommandError("Argument Aliases must be unique")


def find_similar_command(command: Command, namespace_list: list[str]):
    """Finds commands in the command tree that resemble `namespace_list`
    Compares each of their full-qualified names to the provided name with
    the levenshtein algorithm. If it's similar enough (with respect to)
    `config.suggest_levenshtein_distance`, that command_name will be returned
    """
    if config.suggest_on_missing_command:
        namespace_str = config.namespace_sep.join(namespace_list)
        command_names = get_all_command_names(command)

        distance, command_name = min(
            (
                (utils.levenshtein(namespace_str, command_name), command_name)
                for command_name in command_names
            ),
            key=lambda tup: tup[0],
        )

        if distance <= config.suggest_levenshtein_distance:
            return command_name

    return None


def get_all_command_names(
    command: Command, parent_namespace: str = "", root=True
) -> list[str]:
    """Recursively walks down the command tree and
    generates fully-qualified names for all commands

    Args:
        command (Command): Root of the command tree you want to generates
        parent_namespace (str, optional): Parent namespace of `command`. Defaults to "".
        root (bool, optional): Whether or not the consider `command` the root of the namespace.
            Defaults to True.

    Returns:
        list[str]: Names of every command in the command-tree, fully qualified
    """
    if root:
        current = ""
    else:
        current = config.namespace_sep.join((parent_namespace, command.name)).lstrip(
            config.namespace_sep
        )

    names = [current]

    if len(command.subcommands) == 0:
        return names

    for subcommand in command.subcommands.values():
        names += get_all_command_names(subcommand, current, False)

    return names
