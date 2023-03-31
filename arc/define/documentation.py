from __future__ import annotations

import re
import textwrap
import typing as t
from functools import cached_property
from arc import color
from arc.present.markdown import MarkdownParser
from arc.present.markdown.config import MarkdownConfig

import arc.typing as at
from arc.define.param import param
from arc.present.help_formatter import HelpFormatter

if t.TYPE_CHECKING:
    from arc.define.command import Command
    from arc.config import ColorConfig

ParamKinds = t.Literal["argument", "option", "flag"]

KIND_MAPPING: dict[type[param.Param], ParamKinds] = {
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
        default_section_name: str,
        color: ColorConfig,
        description: str = None,
    ):
        self.command = command
        self.default_section_name = default_section_name
        self.color = color
        self._description = description
        self._docstring = textwrap.dedent(self.command.callback.__doc__ or "")
        self.parser = MarkdownParser()

    def help(self) -> str:
        formatter = HelpFormatter(self, self.default_section_name, self.color)
        formatter.write_help()
        content = f"{formatter.value}\n{self.sections}"
        doc = self.parser.parse(content)
        return doc.fmt(MarkdownConfig())

    def usage(self) -> str:
        formatter = HelpFormatter(self, self.default_section_name, self.color)
        formatter.write_usage()
        return formatter.value

    @property
    def fullname(self) -> list[str]:
        return list(c.name for c in self.command.command_chain)[1:]

    @property
    def description(self) -> t.Optional[str]:
        return self._split_sections()[0]

    @property
    def sections(self) -> str:
        return self._split_sections()[1]

    @property
    def short_description(self) -> t.Optional[str]:
        description = self.description
        return description if description is None else description.split("\n")[0]

    @property
    def global_params(self) -> list[ParamDoc]:
        return [
            p
            for p in self._param_helper(self.command.root)
            if p["name"] not in self.command.SPECIAL_PARAMS
        ]

    @property
    def params(self) -> list[ParamDoc]:
        return self._param_helper(self.command)

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

    def _split_sections(self) -> tuple[str, str]:
        desc = ""
        rest = ""

        for idx, char in enumerate(self._docstring):
            if char == "#":
                rest = self._docstring[idx:]
                break

            desc += char

        return desc, rest
