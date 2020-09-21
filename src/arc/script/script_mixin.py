import sys
import inspect
from typing import List, Dict
from contextlib import contextmanager

from arc.parser.data_types import FlagNode
from arc.errors import ScriptError, ExecutionError

import arc._utils as util
from .__option import Option, NO_DEFAULT
from .__flag import Flag


class ScriptMixin:
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

    @staticmethod
    @contextmanager
    def catch():
        """Context Manager to catch and handle errors
        when calling the script's function"""
        try:
            util.logger("---------------------------")
            yield
        except ExecutionError as e:
            print(e)
            sys.exit(1)
        finally:
            util.logger("---------------------------")

    def assert_options_filled(self):
        for option in self.options.values():
            if option.value is NO_DEFAULT:
                raise ScriptError(f"No valued for required option '{option.name}'")

    class ArgBuilder:
        def __init__(self, function):
            self.sig = inspect.signature(function)
            self.length = len(self.sig.parameters.values())
            self.options: Dict[str, Option] = {}
            self.flags: Dict[str, Flag] = {}
            self.param = None
            self.idx = 0

        def __enter__(self):
            return self

        def __exit__(self, *args):
            del self

        def __len__(self):
            return self.length

        def __iter__(self):
            for param in self.sig.parameters.values():
                yield param
                self.add_arg(param)

        def add_arg(self, param):
            if param.annotation is bool:
                self.flags[param.name] = Flag(param)

            elif param.kind not in (param.VAR_KEYWORD, param.VAR_POSITIONAL):
                self.options[param.name] = Option(param)

        @property
        def args(self):
            return self.options, self.flags
