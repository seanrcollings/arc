from __future__ import annotations
import typing as t
from functools import cached_property
import textwrap

import arc.typing as at
from arc.define.param import param

if t.TYPE_CHECKING:
    from arc.present.help_formatter import HelpFormatter
    from arc.define.command import Command
    from arc.config import PresentConfig

ParamKinds = t.Literal["argument", "option", "flag"]

KIND_MAPPING: dict[type[param.Param[t.Any]], ParamKinds] = {
    param.ArgumentParam: "argument",
    param.OptionParam: "option",
    param.FlagParam: "flag",
}


class ParamDoc(t.TypedDict):
    name: str
    short_name: str | None
    description: str | None
    kind: ParamKinds
    optional: bool
    nargs: at.NArgs
    default: t.Any


class Documentation:
    def __init__(
        self,
        command: Command,
        config: PresentConfig,
        description: str = None,
    ):
        self.command = command
        self.config = config
        self._description = description
        self.docstring = self._get_docstring()

    def help(self) -> str:
        formatter = self.config.formatter(self, self.config)
        return formatter.format_help()

    def usage(self) -> str:
        formatter = self.config.formatter(self, self.config)
        return formatter.format_usage()

    @property
    def fullname(self) -> list[str]:
        return list(c.name for c in self.command.command_chain)[1:]

    @property
    def description(self) -> t.Optional[str]:
        return self._split_sections[0]

    @property
    def sections(self) -> str:
        return self._split_sections[1]

    @property
    def short_description(self) -> t.Optional[str]:
        description = self.description
        return description if description is None else description.split("\n")[0]

    @property
    def params(self) -> list[ParamDoc]:
        return self._param_helper(self.command)

    @cached_property
    def _split_sections(self) -> tuple[str, str]:
        desc = ""
        rest = ""

        for idx, char in enumerate(self.docstring):
            if char == "#":
                rest = self.docstring[idx:]
                break

            desc += char

        return desc.strip(), rest.strip()

    def _param_helper(self, command: Command) -> list[ParamDoc]:
        # descriptions = command.doc._parsed_argument_section
        return [
            {
                "name": param.param_name,
                "short_name": param.short_name,
                "description": param.description,
                "kind": KIND_MAPPING[type(param)],
                "optional": param.is_optional,
                "nargs": param.nargs,
                "default": param.default,
            }
            for param in command.cli_params
        ]

    def _get_docstring(self) -> str:
        doc = self.command.callback.__doc__ or self._description or ""
        doc = doc.lstrip()
        # we add some spaces to the beginning of the docstring so that
        # textwrap.dedent removes all of the lines indentation
        doc = " " * 10 + doc
        doc = textwrap.dedent(doc)
        return doc
