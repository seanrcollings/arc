from functools import cached_property
from .param_builder import ParamBuilder


class ParamMixin:
    @cached_property
    def param_groups(self):
        builder = ParamBuilder(self.callback)
        groups = builder.build()

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
