import sys
import inspect
from typing import Dict, Any
from contextlib import contextmanager


from arc.errors import ScriptError, ExecutionError

import arc.utils as util
from .__option import Option, NO_DEFAULT, EMPTY


class ScriptMixin:
    args: Dict[str, Option]
    meta: Any

    # HELPERS

    @staticmethod
    @contextmanager
    def catch():
        """Context Manager to catch and handle errors
        when calling the script's function"""
        # Probably do something different when failing on an ExecutionError and
        # when failing on a general exception
        # Also make this functionality part of Script.__call__ because it shouldn't be optional
        try:
            util.logger.debug("---------------------------")
            yield
        except ExecutionError as e:
            print(e)
            sys.exit(1)
        except Exception as e:
            print(e)
        finally:
            util.logger.debug("---------------------------")

    def assert_args_filled(self):
        for option in self.args.values():
            if option.value is NO_DEFAULT:
                raise ScriptError(f"No value for required option '{option.name}'")

    def add_meta(self):
        if self.meta:
            self.args["meta"] = Option(name="meta", annotation=Any, default=NO_DEFAULT)
            self.args["meta"].value = self.meta

    class ArgBuilder:
        # Make part of the Script Object
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
