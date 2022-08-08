from __future__ import annotations
import argparse
import typing as t
from functools import cached_property
from arc import autocompletions
from arc.autocompletions import completions

from arc.config import config
from arc.parser import CustomAutocompleteAction, CustomHelpAction, CustomVersionAction

from .param import FlagParam, OptionParam, Param
from .param_group import ParamGroup
from .param_builder import ParamBuilder


class ParamMixin:
    SPECIAL_PARAMS = {"help", "version", "autocomplete"}
    callback: t.Callable
    parent: t.Any

    @cached_property
    def param_groups(self) -> list[ParamGroup]:
        builder = ParamBuilder(self.callback)
        groups = builder.build()

        default = ParamGroup.get_default_group(groups)
        if self.is_root and not self.is_namespace:  # type: ignore

            if config.version:
                self.__add_version_param(default)

            if config.autocomplete:
                self.__add_autocomplete_param(default)

        self.__add_help_param(default)

        return groups

    @property
    def params(self):
        for group in self.param_groups:
            yield from group.all_params()

    @property
    def cli_params(self):
        """All params that are available on the command line"""
        for param in self.params:
            if not param.is_injected:
                yield param

    @property
    def argument_params(self):
        for param in self.params:
            if param.is_argument:
                yield param

    @property
    def key_params(self):
        for param in self.params:
            if param.is_keyword:
                yield param

    @property
    def option_params(self):
        for param in self.params:
            if param.is_option:
                yield param

    @property
    def flag_params(self):
        for param in self.params:
            if param.is_flag:
                yield param

    @property
    def injected_params(self):
        for param in self.params:
            if param.is_injected:
                yield param

    def get_param(self, name: str) -> t.Optional[Param]:
        for param in self.params:
            if name in (param.argument_name, param.param_name, param.short_name):
                return param

        return None

    def __add_version_param(self, group: ParamGroup):
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

    def __add_help_param(self, group: ParamGroup):
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

    def __add_autocomplete_param(self, group: ParamGroup):
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
