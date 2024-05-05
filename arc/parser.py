from __future__ import annotations

import argparse
import typing as t
from gettext import gettext as _

import arc
import arc.typing as at
from arc import errors, safe
from arc.autocompletions import ShellCompletion
from arc.color import fg
from arc.define.param import Action, Param
from arc.present.joiner import Join


if t.TYPE_CHECKING:
    from arc.define.command import Command


class Parser(argparse.ArgumentParser):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.param_map: dict[str, Param[t.Any]] = {}

    def parse_intermixed_args(  # type: ignore
        self, args: t.Sequence[str] | None = None, namespace=None
    ) -> at.ParseResult:
        res = super().parse_intermixed_args(args, namespace)
        return dict(res._get_kwargs())

    def parse_known_intermixed_args(  # type: ignore
        self, args: t.Sequence[str] | None = None, namespace=None
    ) -> tuple[at.ParseResult, list[str]]:
        parsed, rest = super().parse_known_intermixed_args(args, namespace)
        return (dict(parsed._get_kwargs()), rest)

    def add_param(self, param: Param[t.Any], command: Command) -> None:
        kwargs: dict[str, t.Any] = {}

        kwargs["action"] = (
            param.action.value if isinstance(param.action, Action) else param.action
        )

        if (default := param.parser_default) is not None:
            kwargs["default"] = default

        if safe.issubclass(param.action, CustomAction):
            kwargs["command"] = command

        if param.action is Action.STORE:
            kwargs["nargs"] = param.nargs

        if not param.is_argument:
            kwargs["dest"] = param.argument_name

        for name in param.get_param_names():
            self.param_map[name] = param

        self.add_argument(*param.get_param_names(), **kwargs)

    # NOTE: This method is called within _parse_known_args of the base class.
    # We override it to modify the error handling behavior
    def _match_argument(self, action: argparse.Action, args_str_pattern: str) -> int:
        try:
            return super()._match_argument(action, args_str_pattern)
        except argparse.ArgumentError as e:
            # TODO: need to verify that this is the only
            # circumstance that this error will be raised given the
            # way in which I'm using argparse
            param = self.param_map[t.cast(str, e.argument_name)]
            raise errors.MissingOptionValueError(param) from e

    def error(self, message: str) -> t.NoReturn:
        raise errors.ParserError(message)

    def exit(self, status: int = 0, message: str | None = None) -> t.NoReturn:
        raise errors.Exit(status, message)


class CustomAction(argparse.Action):
    def __init__(self, *args: t.Any, command: Command, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.command = command


class CustomHelpAction(CustomAction, argparse._HelpAction):
    def __call__(self, *args: t.Any, **kwargs: t.Any) -> None:
        arc.print(self.command.doc.help())
        arc.exit()


class CustomVersionAction(CustomAction, argparse._VersionAction):
    def __call__(self, *args: t.Any, **kwargs: t.Any) -> None:
        arc.print(self.command.config.version)
        arc.exit()


class CustomAutocompleteAction(CustomAction, argparse._StoreAction):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        ns: argparse.Namespace,
        value: t.Any,
        option_string: str | None = None,
    ) -> None:
        print(ShellCompletion.run(value, self.command), end="")
        arc.exit()
