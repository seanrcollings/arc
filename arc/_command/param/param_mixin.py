from __future__ import annotations
import typing as t
from functools import cached_property
from arc.autocompletions import completions

from arc.config import config

from .param import Action, FlagParam, OptionParam
from .param_group import ParamGroup
from .param_builder import ParamBuilder


class ParamMixin:
    SPECIAL_PARAMS = {"help", "version", "autocomplete"}
    callback: t.Callable
    parent: t.Any
    is_namespace: bool
    is_root: bool

    @cached_property
    def param_groups(self) -> list[ParamGroup]:
        builder = ParamBuilder(self.callback)
        groups = builder.build()

        default = ParamGroup.get_default_group(groups)
        if self.is_root and not self.is_namespace:
            self.__add_autocomplete_param(default)

            if config.version:
                self.__add_version_param(default)

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

    def __add_version_param(self, group: ParamGroup):
        def version_callback(_value, ctx, _param):
            print(config.version)
            ctx.exit()

        group.insert(
            0,
            FlagParam(
                "version",
                short_name="v",
                annotation=bool,
                description="Displays the app's version number",
                default=False,
                callback=version_callback,
                action=Action.STORE_TRUE,
                expose=False,
            ),
        )

    def __add_help_param(self, group: ParamGroup):
        def help_callback(_value, ctx, _param):
            print(ctx.command.doc.help())
            ctx.exit()

        group.insert(
            0,
            FlagParam(
                "help",
                short_name="h",
                annotation=bool,
                description="Displays this help message",
                default=False,
                callback=help_callback,
                action=Action.STORE_TRUE,
                expose=False,
            ),
        )

    def __add_autocomplete_param(self, group: ParamGroup):
        def autocomplete_callback(value, ctx, _param):
            completions(value, ctx)
            ctx.exit()

        group.insert(
            0,
            OptionParam(
                "autocomplete",
                annotation=str,
                description="Shell completion support",
                callback=autocomplete_callback,
                default=None,
                expose=False,
            ),
        )
