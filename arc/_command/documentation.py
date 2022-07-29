from __future__ import annotations
from functools import cached_property
import re
import typing as t

from arc.config import config
from arc._command.param import param
from arc.present.help_formatter import HelpFormatter
import arc.typing as at


if t.TYPE_CHECKING:
    from arc.types.type_info import TypeInfo
    from arc._command.command import Command


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
    def __init__(self, command: Command, description: str = None):
        self.command = command
        self._description = description
        self._docstring = self.command.callback.__doc__

    def help(self):
        formatter = HelpFormatter(self)
        formatter.write_help()
        return formatter.value

    def usage(self):
        formatter = HelpFormatter(self)
        formatter.write_usage()
        return formatter.value

    @property
    def fullname(self):
        names = []
        command = self.command
        while command.parent:
            names.append(command.name)
            command = command.parent

        return list(reversed(names))

    @property
    def description(self) -> t.Optional[str]:
        return self._description or self.docstring.get(config.default_section_name)

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
        descriptions = command.doc._parsed_argument_section
        return [
            {
                "name": param.param_name,
                "short_name": param.short_name,
                "description": param.description
                or descriptions.get(param.argument_name),
                "kind": KIND_MAPPING[type(param)],
                "optional": param.is_optional,
                "nargs": param.nargs,
                "default": param.default,
            }
            for param in command.cli_params
        ]

    @cached_property
    def docstring(self):
        """Parsed docstring for the command
        Sections are denoted by a new line, and
        then a line beginning with `#`. Whatever
        comes after the `#` will be the key in
        the sections dict. And all content between
        that `#` and the next `#` will be the value.
        The first section of the docstring is not
        required to possess a section header, and
        will be entered in as the `description` section.
        """
        if not self._docstring:
            return {}

        parsed: dict[str, str] = {config.default_section_name: ""}
        lines = [line.strip() for line in self._docstring.split("\n")]

        current_section = config.default_section_name

        for line in lines:
            if line.startswith("#"):
                current_section = line[1:].strip().lower()
                parsed[current_section] = ""
            else:
                parsed[current_section] += line + "\n"

        return {key: value.strip() for key, value in parsed.items()}

    @cached_property
    def _parsed_argument_section(self) -> dict[str, str]:
        arguments = self.docstring.get("arguments")
        if not arguments:
            return {}

        parsed: dict[str, str] = {}
        regex = re.compile(r"^\w+:.+")
        current_param = ""

        for line in arguments.splitlines():
            if regex.match(line):
                param, first_line = line.split(":", maxsplit=1)
                current_param = param
                parsed[current_param] = first_line.strip()
            elif current_param:
                parsed[current_param] += " " + line.strip()

        return parsed
