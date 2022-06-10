from __future__ import annotations
import argparse
import typing as t
from arc._command.param import Action, Param
from arc.constants import MISSING
import arc.typing as at


class Parser(argparse.ArgumentParser):
    def parse_intermixed_args(  # type: ignore
        self, args: t.Sequence[str] | None = None, namespace=None
    ) -> at.ParseResult:
        res = super().parse_intermixed_args(args, namespace)
        return dict(res._get_kwargs())

    def add_param(self, param: Param):
        kwargs: dict[str, t.Any] = {"action": param.action.value, "default": MISSING}

        if param.action is Action.STORE:
            kwargs["nargs"] = param.nargs

        self.add_argument(*param.get_param_names(), **kwargs)
