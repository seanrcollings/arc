from __future__ import annotations

import typing as t
from functools import cached_property

from arc import autocompletions
from arc.define.alias import AliasDict
from arc.parser import CustomAutocompleteAction, CustomHelpAction, CustomVersionAction

from .param_definition import ParamDefinition, ParamDefinitionFactory
from .param import FlagParam, OptionParam, Param

if t.TYPE_CHECKING:
    from arc.config import Config


class ParamMixin:
    SPECIAL_PARAMS = {"help", "version", "autocomplete"}
    callback: t.Callable
    parent: t.Any
    config: Config

    @cached_property
    def param_def(self) -> ParamDefinition:
        root = ParamDefinitionFactory(self.config.transform_snake_case).from_function(
            self.callback
        )

        # TODO: Move adding these to runtime
        if self.is_root and not self.is_namespace:  # type: ignore

            if self.config.version:
                self.__add_version_param(root)

            if self.config.autocomplete:
                self.__add_autocomplete_param(root)

        self.__add_help_param(root)

        return root

    @cached_property
    def param_map(self) -> t.Mapping[str, Param]:
        data: AliasDict[str, Param] = AliasDict()
        for param in self.params:
            data[param.argument_name] = param
            data.add_alias(param.argument_name, param.param_name)
            if param.short_name:
                data.add_alias(param.argument_name, param.short_name)
            data.add_aliases(param.argument_name, *param.get_param_names())

        return data

    @property
    def params(self) -> t.Generator[Param, None, None]:
        yield from self.param_def.all_params()

    @property
    def cli_params(self) -> t.Generator[Param, None, None]:
        """All params that are available on the command line"""
        for param in self.params:
            if not param.is_injected:
                yield param

    @property
    def argument_params(self) -> t.Generator[Param, None, None]:
        for param in self.params:
            if param.is_argument:
                yield param

    @property
    def key_params(self) -> t.Generator[Param, None, None]:
        for param in self.params:
            if param.is_keyword:
                yield param

    @property
    def option_params(self) -> t.Generator[Param, None, None]:
        for param in self.params:
            if param.is_option:
                yield param

    @property
    def flag_params(self) -> t.Generator[Param, None, None]:
        for param in self.params:
            if param.is_flag:
                yield param

    @property
    def injected_params(self) -> t.Generator[Param, None, None]:
        for param in self.params:
            if param.is_injected:
                yield param

    def get_param(self, name: str) -> t.Optional[Param]:
        return self.param_map.get(name)

    def __add_version_param(self, group: ParamDefinition):
        group.append(
            FlagParam(
                "version",
                short_name="v",
                annotation=bool,
                description="Displays the app's version number",
                default=False,
                action=CustomVersionAction,
                expose=False,
            ),
        )

    def __add_help_param(self, group: ParamDefinition):
        group.insert(
            0,
            FlagParam(
                "help",
                short_name="h",
                annotation=bool,
                description="Displays this help message",
                default=False,
                action=CustomHelpAction,
                expose=False,
            ),
        )

    def __add_autocomplete_param(self, group: ParamDefinition):
        annotation = t.Literal[1]
        annotation.__args__ = tuple(autocompletions.shells.keys())  # type: ignore
        group.append(
            OptionParam(
                "autocomplete",
                annotation=annotation,  # type: ignore
                description="Shell completion support",
                action=CustomAutocompleteAction,
                default=None,
                expose=False,
            ),
        )
