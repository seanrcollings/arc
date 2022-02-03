"""Mixin for param properties and functions
Note that in development, all parameters are insantiated, but
in production only the command being executed parameters are
created.
"""
from __future__ import annotations
import functools
import typing as t

from arc.autocompletions import completions

if t.TYPE_CHECKING:
    from arc._command.param_builder import ParamBuilder

from arc._command.param import Flag, Param, Option


def _help_callback(value, ctx, _param):
    if value:
        print(ctx.command.get_help(ctx))
        ctx.exit()


class ParamMixin:
    builder: type[ParamBuilder]
    _autocomplete: bool

    @functools.cached_property
    def params(self) -> list[Param]:
        params = self.builder(self._callback).build()  # type: ignore
        params.insert(
            0,
            Flag(
                "help",
                short="h",
                description="Shows help documentation",
                callback=_help_callback,
                expose=False,
            ),
        )

        if self._autocomplete:

            def _autocomplete_callback(value: str, ctx, _param):
                if value:
                    completions(value, ctx)
                    ctx.exit()

            params.append(
                Option(
                    "autocomplete",
                    annotation=str,
                    description="Generates auto completions for the CLI",
                    callback=_autocomplete_callback,
                    default=None,
                    expose=False,
                )
            )

        return params

    @functools.cached_property
    def pos_params(self) -> list[Param]:
        return [param for param in self.params if param.is_positional]

    @functools.cached_property
    def key_params(self) -> list[Param]:
        return self.flag_params + self.option_params

    @functools.cached_property
    def option_params(self) -> list[Param]:
        return [param for param in self.params if param.is_option]

    @functools.cached_property
    def flag_params(self) -> list[Param]:
        return [param for param in self.params if param.is_flag]

    @functools.cached_property
    def special_params(self) -> list[Param]:
        return [param for param in self.params if param.is_special]

    @functools.cached_property
    def visible_params(self) -> list[Param]:
        """Params that will be visible to the command line"""
        return [param for param in self.params if not param.hidden]

    @functools.cached_property
    def optional_params(self) -> list[Param]:
        """Optional params have a default value"""
        return [param for param in self.params if param.optional]

    @functools.cached_property
    def required_params(self) -> list[Param]:
        """Required params do not have a default value"""
        return [param for param in self.params if not param.optional]

    def get_param(self, name: str, visible: bool = True) -> t.Optional[Param]:
        for param in self.params:
            if name in (param.arg_alias, param.arg_name):
                if visible and param.hidden:
                    return None
                return param

        return None
