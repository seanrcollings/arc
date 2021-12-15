"""Mixin for param properties and functions
Note that in development, all paramaters are insantiated, but
in production only the command being executed parameters are
created.
"""
import functools
from typing import Callable
from arc.command.param_builder import ParamBuilder
from arc.command.param import Param


class ParamMixin:
    builder: type[ParamBuilder]

    @functools.cached_property
    def params(self) -> dict[str, Param]:
        return self.builder(self.callback).build()  # type: ignore

    @functools.cached_property
    def pos_params(self) -> dict[str, Param]:
        return {key: param for key, param in self.params.items() if param.is_positional}

    @functools.cached_property
    def key_params(self) -> dict[str, Param]:
        return {key: param for key, param in self.params.items() if param.is_keyword}

    @functools.cached_property
    def flag_params(self) -> dict[str, Param]:
        return {key: param for key, param in self.params.items() if param.is_flag}

    @functools.cached_property
    def special_params(self) -> dict[str, Param]:
        return {key: param for key, param in self.params.items() if param.is_special}

    @functools.cached_property
    def visible_params(self) -> dict[str, Param]:
        return {
            key: param for key, param in self.params.items() if not param.is_special
        }

    @functools.cached_property
    def optional_params(self) -> dict[str, Param]:
        return {key: param for key, param in self.params.items() if param.optional}

    @functools.cached_property
    def required_params(self) -> dict[str, Param]:
        return {key: param for key, param in self.params.items() if not param.optional}
