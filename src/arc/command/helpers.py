import inspect
from typing import Dict, Any

from arc.errors import CommandError

from .__option import Option, NO_DEFAULT, EMPTY


class CommandMixin:
    args: Dict[str, Option]
    meta: Any

    # HELPERS

    def assert_args_filled(self):
        for option in self.args.values():
            if option.value is NO_DEFAULT:
                raise CommandError(f"No value for required option '{option.name}'")

    def add_meta(self):
        if self.meta:
            self.args["meta"] = Option(name="meta", annotation=Any, default=NO_DEFAULT)
            self.args["meta"].value = self.meta


class ArgBuilder:
    def __init__(self, function):
        self.__sig = inspect.signature(function)
        self.__length = len(self.__sig.parameters.values())
        self.__args: Dict[str, Option] = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self

    def __len__(self):
        return self.__length

    def __iter__(self):
        for param in self.__sig.parameters.values():
            yield param
            self.add_arg(param)

    @property
    def args(self):
        return self.__args

    def add_arg(self, param: inspect.Parameter):
        if param.annotation is bool:
            default = False if param.default is EMPTY else param.default
            self.__args[param.name] = Option(param.name, param.annotation, default)

        elif param.kind not in (param.VAR_KEYWORD, param.VAR_POSITIONAL):
            self.__args[param.name] = Option(
                param.name, param.annotation, param.default
            )

    def get_meta(self, **kwargs):
        return dict(length=self.__length, **kwargs)
