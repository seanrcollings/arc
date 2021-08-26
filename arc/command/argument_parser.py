from __future__ import annotations
from typing import Callable, Any, Optional, Union, TypedDict, TYPE_CHECKING
import re

from arc import errors
from arc.config import config
from arc.color import colorize, fg, effects
from arc.utils import IDENT, levenshtein
from arc.command.param import Param

if TYPE_CHECKING:
    from arc.command.executable import Executable


class Parsed(TypedDict):
    pos_args: list[Any]
    options: dict[str, Any]
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
        # if isinstance(groups, dict):
        #     groups = {key: value.replace("-", "_") for key, value in groups.items()}
        # else:
        #     groups = groups.replace("-", "_")

        handler: Callable = getattr(self, f"handle_{name}")
        try:
            return handler(groups)
        except errors.MissingArgError as e:
            arg = self.find_argument_suggestions(e.data["name"])
            if arg:
                e.message += (
                    f"\n\tPerhaps you meant {fg.YELLOW}{arg.arg_alias}{effects.CLEAR}?"
                )
            raise

    def handle_option(self, option: str):
        if self.pos_only:
            raise errors.ParserError(
                "Options are not allowed after "
                f"{colorize(config.flag_denoter, fg.YELLOW)} if it is present"
            )

        try:
            arg = self.executable.get_or_raise(
                option, f"Option {colorize('--' + option, fg.YELLOW)} not found."
            )
            if arg.is_flag:
                self.parsed["flags"].append(arg.arg_alias)
            elif self.peek():
                value = self.consume()
                self.parsed["options"][arg.arg_alias] = value
            else:
                raise errors.ParserError(
                    f"Option {colorize('--' + option, fg.YELLOW)} requires a value"
                )
        except errors.MissingArgError as e:
            if self.peek():
                value = self.consume()
                self.parsed["options"][option] = value
            else:
                raise errors.ParserError(
                    f"Option {colorize('--' + option, fg.YELLOW)} requires a value"
                ) from e

    def handle_short_option(self, short_option):
        for char in short_option:
            # try:
            arg = self.executable.get_or_raise(
                char, f"Option {colorize('-' + short_option, fg.YELLOW)} not found."
            )
            if len(short_option) > 1 and not arg.is_flag:
                raise errors.ParserError(
                    f"Option {colorize('-' + char, fg.YELLOW)} requires a value"
                )

            self.handle_option(arg.arg_alias)
            # except errors.MissingArgError as e:
            #     if self.peek():
            #         value = self.consume()
            #         self.parsed["options"][short_option] = value
            #     else:
            #         raise errors.ParserError(
            #             f"Option {colorize('-' + char, fg.YELLOW)} requires a value"
            #         ) from e

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

    def find_argument_suggestions(self, missing: str) -> Optional[Param]:
        visible_args = [
            param for param in self.executable.params.values() if not param.hidden
        ]
        if config.suggest_on_missing_argument and len(visible_args) > 0:
            distance, arg = min(
                (
                    (levenshtein(param.arg_alias, missing), param)
                    for param in visible_args
                ),
                key=lambda tup: tup[0],
            )

            if distance <= config.suggest_levenshtein_distance:
                return arg

        return None
