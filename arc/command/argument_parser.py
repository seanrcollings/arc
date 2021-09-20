from __future__ import annotations
from typing import Callable, Any, Union, TypedDict, TYPE_CHECKING
import re

from arc import errors
from arc.config import config
from arc.color import colorize, fg
from arc.utils import IDENT


if TYPE_CHECKING:
    from arc.command.executable import Executable


class Parsed(TypedDict):
    pos_args: list[str]
    options: dict[str, str]
    flags: list[str]


class ArgumentParser:
    matchers = {
        "option": re.compile(fr"^{config.flag_denoter}({IDENT})$"),
        "short_option": re.compile(fr"^{config.short_flag_denoter}([a-zA-Z]+)$"),
        "pos_only": re.compile(fr"^({config.flag_denoter})$"),
        "value": re.compile(r"^(.+)$"),
    }

    to_parse: list[str]

    def __init__(self, executable: Executable):
        self.executable = executable
        self.pos_only = False
        self.parsed: Parsed = {
            "pos_args": [],
            "options": {},
            "flags": [],
        }

    def parse(self, to_parse: list[str]):
        self.to_parse = to_parse.copy()
        while len(self.to_parse) > 0:
            curr_token = self.consume()
            for name, regex in self.matchers.items():
                if match := regex.match(curr_token):
                    self.handle_match(match, name)
                    break
            else:
                raise errors.ParserError(f"Could not parse {curr_token}")

        parsed = self.parsed
        self.parsed = {"pos_args": [], "options": {}, "flags": []}
        return parsed

    ### Handlers ###
    def handle_match(self, match: re.Match, name: str) -> tuple[str, Any]:
        groups: Union[dict[str, str], str] = self.get_match_values(match)
        handler: Callable = getattr(self, f"handle_{name}")
        return handler(groups)

    def handle_option(self, option: str):
        if self.pos_only:
            raise errors.ParserError(
                "Options are not allowed after "
                f"{colorize(config.flag_denoter, fg.YELLOW)} if it is present"
            )

        try:
            param = self.executable.get_or_raise(
                option, f"Option {colorize('--' + option, fg.YELLOW)} not found."
            )
            if param.is_flag:
                self.parsed["flags"].append(param.arg_alias)
            elif self.peek():
                value = self.consume()
                self.parsed["options"][param.arg_alias] = value
            else:
                raise errors.ParserError(
                    f"Option {colorize('--' + option, fg.YELLOW)} requires a value"
                )
        except errors.MissingArgError:
            if self.peek() and not self.peek().startswith(config.flag_denoter):
                value = self.consume()
                self.parsed["options"][option] = value
            else:
                self.parsed["flags"].append(option)

    def handle_short_option(self, short_option):
        for char in short_option:
            param = self.executable.get_or_raise(
                char, f"Option {colorize('-' + short_option, fg.YELLOW)} not found."
            )
            if len(short_option) > 1 and not param.is_flag:
                raise errors.ParserError(
                    f"Option {colorize('-' + char, fg.YELLOW)} requires a value"
                )

            self.handle_option(param.arg_alias)

    def handle_pos_only(self, _):
        self.pos_only = True
        if len(self.parsed["pos_args"]) > 0:
            raise errors.ParserError(
                "Positional arguments must be placed after "
                f"{colorize(config.flag_denoter, fg.YELLOW)} if it is present"
            )

    def handle_value(self, value):
        self.parsed["pos_args"].append(value)

    ### Helpers ###

    def peek(self):
        if len(self.to_parse) == 0:
            return None

        return self.to_parse[0]

    def consume(self):
        return self.to_parse.pop(0)

    @staticmethod
    def get_match_values(match: re.Match) -> Union[dict[str, str], str]:
        if groups := match.groupdict():
            return groups

        return match.groups()[0]
