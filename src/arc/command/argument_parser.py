from typing import Callable, Any, Union, TypedDict
from inspect import Parameter
import re

from arc import arc_config, errors
from arc.color import fg, effects
from arc.utils import IDENT
from .helpers import ArgBuilder
from .argument import Argument, NO_DEFAULT
from .context import Context

# TODO: reimplement kebab-case
class ArgumentParser:
    """Base class for ArgumentParsers

    Handles analyzing the provided function signature to generate
    The Argument data structure

    Attempts to match provided data to `cls.matchers` regexes. If it finds a match,
    it'll pass control over to the match handler (`handle_<matcher-name>`). This class
    should not be used to parse anything, as it does not provide any matchers or handlers
    of it's own.
    """

    def __init__(self, function: Callable):
        self.args: dict[str, Argument] = {}
        self.build_args(function)

    def get_matchers(self):
        all_matchers = {}
        for cls in reversed(self.__class__.mro()):
            if matchers := getattr(cls, "matchers", None):
                all_matchers |= matchers

        return all_matchers

    ### Argument Parsing ###

    def parse(self, cli_args: list[str], context: dict[str, Any]) -> dict[str, Any]:
        """Parses the provided command-line arguments into
        a dictionary of arguments to be passed to a python
        function
        """
        matchers = self.get_matchers()
        matched_args: dict[str, Any] = {}
        for cli_arg in cli_args:
            for name, regex in matchers.items():
                if match := regex.match(cli_arg):
                    key, value = self.handle_match(match, name)
                    if any((key, value)):
                        matched_args[key] = value

        return self.fill_unmatched(matched_args, context)

    def handle_match(self, match: re.Match, name: str) -> tuple[str, Any]:
        groups: Union[dict[str, str], str] = self.get_match_values(match)
        handler: Callable = getattr(self, f"handle_{name}")
        return handler(groups)

    def fill_unmatched(
        self, matched_args: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:

        unfilled = {}
        for key, arg in self.args.items():
            if key not in matched_args:
                if issubclass(arg.annotation, Context):
                    unfilled[key] = arg.annotation(context)
                else:
                    unfilled[key] = arg.default

        for key, value in unfilled.items():
            if value is NO_DEFAULT:
                raise errors.ParserError(
                    "No value provided for required argument: "
                    f"{fg.YELLOW}{key}{effects.CLEAR}"
                )

        return matched_args | unfilled

    ### Argument Schema Building ###

    def build_args(self, function: Callable):
        with ArgBuilder(function) as builder:
            for idx, param in enumerate(builder):
                self.arg_hook(param, builder.get_meta(index=idx))

            self.args = builder.args

    def arg_hook(self, param, meta):
        """Callback to assert that the param being processed
        is valid for this given parser. Default implementation
        doesn't do anything
        """

    ### Helpers ###

    def get_or_raise(self, key: str, message):
        arg = self.args.get(key)
        if arg and not arg.hidden:
            return arg

        raise errors.ParserError(message)

    @staticmethod
    def get_match_values(match: re.Match) -> Union[dict[str, str], str]:
        if groups := match.groupdict():
            return groups

        return match.group(1)


FLAG = re.compile(fr"\A{arc_config.flag_denoter}(?P<name>\b{IDENT})$")


class FlagParser(ArgumentParser):
    """Class to handle parsing out the `--flags`"""

    matchers = {"flag": FLAG}

    def handle_flag(self, flag: dict[str, str]) -> tuple[str, Any]:
        arg = self.get_or_raise(
            flag["name"], f"Flag {arc_config.flag_denoter}{flag['name']} not recognized"
        )
        return arg.name, not arg.default


# pylint: disable=inherit-non-class
class KeyArg(TypedDict):
    name: str
    value: str


KEY_ARGUMENT = re.compile(
    fr"\A\b(?P<name>{IDENT}\b){arc_config.arg_assignment}(?P<value>.+)$"
)


class KeywordParser(FlagParser):
    __pass_kwargs: bool = False

    matchers = {"keyword_argument": KEY_ARGUMENT}

    def handle_keyword_argument(self, argument: KeyArg) -> tuple[str, Any]:
        name = argument["name"].replace("-", "_")
        try:
            arg = self.get_or_raise(
                name,
                f"Argument {argument['name']}{arc_config.arg_assignment}"
                f"{argument['value']} not recognized",
            )
            name = arg.name
            value = arg.convert(argument["value"])
        except errors.ParserError:
            if self.__pass_kwargs:
                name = name
                value = argument["value"]
            else:
                raise

        return name, value

    def arg_hook(self, param: Parameter, meta):
        idx = meta["index"]

        if param.kind is param.VAR_POSITIONAL:
            raise errors.CommandError(
                "Keyword commands do not allow *args.",
                "If you wish to use it, change the argument type to POSITIONAL",
                "However, be aware that this will",
                "make ALL arguments passed by position rather than keyword",
            )

        if param.kind is param.VAR_KEYWORD:
            if idx != meta["length"] - 1:
                raise errors.CommandError(
                    "The variable keyword argument (**kwargs)",
                    "must be the last argument of the command",
                )

            self.__pass_kwargs = True


# NOTE: This currently also matches to flags
# because the flag matcher matches before the pos_argument one
# it doesn't error, but could in the future.
POS_ARGUMENT = re.compile(r"\A(.+)$")


class PositionalParser(FlagParser):
    __pass_args = False
    matchers = {"positional_argument": POS_ARGUMENT}
    current_pos = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.non_flags = {
            key: val for key, val in self.args.items() if val.annotation != bool
        }
        self.var_args: list[str] = []

    def parse(self, *args):
        self.current_pos = 0
        parsed = super().parse(*args)
        if self.__pass_args:
            parsed["_args"] = self.var_args

        return parsed

    def handle_positional_argument(self, value: str):
        if self.current_pos >= len(self.non_flags):
            if self.__pass_args:
                self.var_args.append(value)
                return None, None
            else:
                raise errors.ParserError(
                    f"Command takes {len(self.non_flags)} arguments, "
                    f"but was given {self.current_pos + 1}"
                )

        name = list(self.non_flags.keys())[self.current_pos]
        argument = list(self.non_flags.values())[self.current_pos]
        self.current_pos += 1
        return name, argument.convert(value)

    def arg_hook(self, param, meta):
        idx = meta["index"]

        if param.kind is param.VAR_KEYWORD:
            raise errors.CommandError(
                "Positional Arc scripts do not allow **kwargs.",
                "If you wish to use it, change the command type to KEYWORD",
                "in @cli.command. However, be aware that this will",
                "make ALL options passed by keyword rather than position",
            )

        if param.kind is param.VAR_POSITIONAL:
            if idx != meta["length"] - 1:
                raise errors.CommandError(
                    "The variable postional arguement (*args)",
                    "must be the last argument of the command",
                )

            self.__pass_args = True


class RawParser(ArgumentParser):
    ...


class ParsingMethod:
    KEYWORD = KeywordParser
    POSITIONAL = PositionalParser
    RAW = RawParser
    FLAG = FlagParser
