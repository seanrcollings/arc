"""Mixin for param properties and functions
Note that in development, all paramaters are insantiated, but
in production only the command being executed parameters are
created.
"""
import functools
from arc._command.param_builder import ParamBuilder
from arc._command.param import FlagParam, Param


def _help_callback(value, ctx, param):
    if value:
        print(ctx.command.get_help(ctx))
        ctx.exit()


class ParamMixin:
    builder: type[ParamBuilder]

    @functools.cached_property
    def params(self) -> list[Param]:
        params = self.builder(self.callback).build()  # type: ignore
        params.insert(
            0,
            FlagParam(
                "help",
                bool,
                short="h",
                description="Shows help documentation",
                callback=_help_callback,
                expose=False,
            ),
        )

        return params

    @functools.cached_property
    def pos_params(self) -> list[Param]:
        return [param for param in self.params if param.is_positional]

    @functools.cached_property
    def key_params(self) -> list[Param]:
        return [param for param in self.params if param.is_keyword]

    @functools.cached_property
    def flag_params(self) -> list[Param]:
        return [param for param in self.params if param.is_flag]

    @functools.cached_property
    def special_params(self) -> list[Param]:
        return [param for param in self.params if param.is_special]

    @functools.cached_property
    def visible_params(self) -> list[Param]:
        return [param for param in self.params if not param.hidden]

    @functools.cached_property
    def optional_params(self) -> list[Param]:
        return [param for param in self.params if param.optional]

    @functools.cached_property
    def required_params(self) -> list[Param]:
        return [param for param in self.params if not param.optional]
