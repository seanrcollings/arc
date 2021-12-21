from typing import Optional
from arc.command.param_builder import ParamBuilder
from arc.command.param import Param
from arc.types.params import MISSING


class ParamMixin:
    builder: type[ParamBuilder]

    def __init__(self):
        # Params aren't constructed until
        # a command is actually executed
        self._params: Optional[dict[str, Param]] = None
        self._pos_params: dict[str, Param] = {}
        self._key_params: dict[str, Param] = {}
        self._flag_params: dict[str, Param] = {}
        self._optional_params: dict[str, Param] = {}
        self._required_params: dict[str, Param] = {}
        self._hidden_params: dict[str, Param] = {}
        self._special_params: dict[str, Param] = {}
        self._var_pos_param: Optional[Param] = MISSING  # type: ignore
        self._var_key_param: Optional[Param] = MISSING  # type: ignore

    @property
    def params(self):
        if self._params is None:
            self._params = self.builder(self).build()

        return self._params

    @property
    def pos_params(self):
        if not self._pos_params:
            self._pos_params = {
                key: param
                for key, param in self.params.items()
                if param.is_positional and not param.hidden
            }
        return self._pos_params

    @property
    def key_params(self):
        if not self._key_params:
            self._key_params = {
                key: param
                for key, param in self.params.items()
                if param.is_keyword and not param.hidden
            }
        return self._key_params

    @property
    def flag_params(self):
        if not self._flag_params:
            self._flag_params = {
                key: param
                for key, param in self.params.items()
                if param.is_flag and not param.hidden
            }
        return self._flag_params

    @property
    def special_params(self):
        if not self._special_params:
            self._special_params = {
                key: param for key, param in self.params.items() if param.is_special
            }
        return self._special_params

    @property
    def optional_params(self):
        if not self._optional_params:
            self._optional_params = {
                key: param
                for key, param in self.params.items()
                if param.optional and not param.hidden
            }
        return self._optional_params

    @property
    def required_params(self):
        if not self._required_params:
            self._required_params = {
                key: param
                for key, param in self.params.items()
                if not param.optional and not param.hidden
            }
        return self._required_params

    @property
    def hidden_params(self):
        if not self._hidden_params:
            self._hidden_params = {
                key: param for key, param in self.params.items() if param.hidden
            }
        return self._hidden_params
