import sys
import inspect
from typing import List, Dict, Any
from contextlib import contextmanager

from arc.parser.data_types import FlagNode
from arc.errors import ScriptError, ExecutionError

import arc.utils as util
from .__option import Option, NO_DEFAULT
from .__flag import Flag


class ScriptMixin:
    options: Dict[str, Option]
    meta: Any

    def _match_flags(self, flag_nodes: List[FlagNode]):
        """Get's the final flag values to pass to the script

        Compares the FlagNodes given with self.flags
        if they are present in both, the flag is set to True,
        if it is absent from the Nodes it is set to false

        :param flag_nodes: list of FlagNodes from the parser

        :raises ScriptError: if a flag is present in FlagNodes, but
        not in self.flags
        """
        for flag in flag_nodes:
            if flag.name in self.flags:  # type: ignore
                self.flags[flag.name].reverse()  # type: ignore
            else:
                raise ScriptError(f"Flag '{flag.name}' not recognized'")

    # HELPERS

    def assert_options_filled(self):
        for option in self.options.values():
            if option.value is NO_DEFAULT:
                raise ScriptError(f"No value for required option '{option.name}'")

    def add_meta(self):
        if self.meta:
            self.options["meta"] = Option(
                name="meta", annotation=Any, default=NO_DEFAULT
            )
            self.options["meta"].value = self.meta

    class ArgBuilder:
        def __init__(self, function):
            self.__sig = inspect.signature(function)
            self.__length = len(self.__sig.parameters.values())
            self.__options: Dict[str, Option] = {}
            self.__flags: Dict[str, Flag] = {}

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
            return self.__options, self.__flags

        def add_arg(self, param: inspect.Parameter):
            if param.annotation is bool:
                self.__flags[param.name] = Flag(param)

            elif param.kind not in (param.VAR_KEYWORD, param.VAR_POSITIONAL):
                self.__options[param.name] = Option(
                    param.name, param.annotation, param.default
                )

        def get_meta(self, **kwargs):
            return dict(length=self.__length, **kwargs)
