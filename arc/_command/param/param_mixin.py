from functools import cached_property

from arc.config import config

from .param import Action, FlagParam
from .param_group import ParamGroup
from .param_builder import ParamBuilder


class ParamMixin:
    @cached_property
    def param_groups(self):
        builder = ParamBuilder(self.callback)
        groups = builder.build()

        default = ParamGroup.get_default_group(groups)
        if config.version and self.parent is None:

            def _version_callback(value, ctx, param):
                print(config.version)
                ctx.exit()

            default.insert(
                0,
                FlagParam(
                    "version",
                    short_name="v",
                    annotation=bool,
                    description="Displays the version number",
                    default=False,
                    callback=_version_callback,
                    action=Action.STORE_TRUE,
                    expose=False,
                ),
            )

        def _help_callback(value, ctx, param):
            print("show help")
            ctx.exit()

        default.insert(
            0,
            FlagParam(
                "help",
                short_name="h",
                annotation=bool,
                description="Displays the help",
                default=False,
                callback=_help_callback,
                action=Action.STORE_TRUE,
                expose=False,
            ),
        )

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
    def injected_params(self):
        for param in self.params:
            if param.is_injected:
                yield param
