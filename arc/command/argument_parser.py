from __future__ import annotations
from typing import Callable, Any, Optional, Union, TypedDict, Type, TYPE_CHECKING
from inspect import Parameter
import re

from arc import errors
from arc.config import config
from arc.color import fg, effects
from arc.utils import IDENT, levenshtein
from arc.command.argument import Argument, NO_DEFAULT

if TYPE_CHECKING:
    from arc.command.executable import Executable


class ArgumentParser:
    """Base class for ArgumentParsers

    Handles analyzing the provided function signature to generate
    The Argument data structure

    Attempts to match provided data to `cls.matchers` regexes. If it finds a match,
    it'll pass control over to the match handler (`handle_<matcher-name>`). This class
    should not be used to parse anything, as it does not provide any matchers or handlers
    of it's own.
    """

    def __init__(self, executable: Executable):
        self.executable = executable
        self.args = executable.args

    def get_matchers(self):
        all_matchers = {}
        for cls in reversed(self.__class__.mro()):
            if matchers := getattr(cls, "matchers", None):
                all_matchers |= matchers

        return all_matchers

    ### Argument Parsing ###

    def parse(self, cli_args: list[str]) -> dict[str, Any]:
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
                    break

        return matched_args

    def handle_match(self, match: re.Match, name: str) -> tuple[str, Any]:
        groups: Union[dict[str, str], str] = self.get_match_values(match)
        if isinstance(groups, dict):
            groups = {key: value.replace("-", "_") for key, value in groups.items()}
        else:
            groups = groups.replace("-", "_")

        handler: Callable = getattr(self, f"handle_{name}")
        try:
            return handler(groups)
        except errors.MissingArgError as e:
            arg = self.find_argument_suggestions(e.data["name"])
            if arg:
                e.message += (
                    f"\n\tPerhaps you meant {fg.YELLOW}{arg.name}{effects.CLEAR}?"
                )
            raise

    @classmethod
    def arg_hook(cls, param, meta):
        """Callback to assert that the param being processed
        is valid for this given parser. Default implementation
        doesn't do anything
        """

    ### Helpers ###

    def get_or_raise(self, key: str, message):
        arg = self.args.get(key)
        if arg and not arg.hidden:
            return arg

        for arg in self.args.values():
            if key == arg.short and not arg.hidden:
                return arg

        raise errors.MissingArgError(message, name=key)

    @staticmethod
    def get_match_values(match: re.Match) -> Union[dict[str, str], str]:
        if groups := match.groupdict():
            return groups

        return match.group()

    def find_argument_suggestions(self, missing: str) -> Optional[Argument]:

        if config.suggest_on_missing_argument and len(self.args) > 0:
            distance, arg = min(
                ((levenshtein(arg.name, missing), arg) for arg in self.args.values()),
                key=lambda tup: tup[0],
            )

            if distance <= config.suggest_levenshtein_distance:
                return arg

        return None


class FlagParser(ArgumentParser):
    """Class to handle parsing out the `--flags` or `-f`"""

    matchers = {
        "flag": re.compile(
            fr"^(?:{config.flag_denoter}|{config.short_flag_denoter})(?P<name>\b{IDENT})$"
        )
    }

    def handle_flag(self, flag: dict[str, str]) -> tuple[str, Any]:
        name = flag["name"]

        if len(name) == 1:
            flag_denoter = config.short_flag_denoter
        else:
            flag_denoter = config.flag_denoter

        arg = self.get_or_raise(
            name, f"Flag {fg.YELLOW}{flag_denoter}{name}{effects.CLEAR} not recognized"
        )

        if not arg.is_flag():
            raise errors.CommandError(
                f"Argument {fg.YELLOW}{name}{effects.CLEAR} requires a value"
            )

        return arg.name, not arg.default


class StandardParser(FlagParser):
    __pass_kwargs: bool = False
    matchers = {
        "value": re.compile("^(.+)$"),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_arg = None
        self.current_value: str = ""

    def handle_flag(self, flag):
        name = flag["name"]
        try:
            arg = self.get_arg(name)
        except errors.MissingArgError:
            if not self.__pass_kwargs:
                raise
            self.args[name] = Argument(name, str, NO_DEFAULT)
            arg = self.get_arg(name)

        self.current_arg = arg
        self.current_value = ""
        if arg.is_flag():
            return arg.name, not arg.default

        return arg.name, arg.default

    def handle_value(self, value):
        self.current_value += " " + value
        if not self.current_arg:
            raise errors.ParserError("Values must come after options")

        return self.current_arg.name, self.current_arg.convert(
            self.current_value.strip()
        )

    def get_arg(self, name):
        return self.get_or_raise(name, f"Option {config.flag_denoter}{name} not found.")

    @classmethod
    def arg_hook(cls, param, meta):
        if param.kind is param.VAR_POSITIONAL:
            raise errors.CommandError("Standard Commands do not accept *args")
        if param.kind is param.VAR_KEYWORD:
            cls.__pass_kwargs = True


# pylint: disable=inherit-non-class
class KeyArg(TypedDict):
    name: str
    value: str


KEY_ARGUMENT = re.compile(
    fr"\A\b(?P<name>{IDENT}\b){config.arg_assignment}(?P<value>.+)$"
)


class KeywordParser(FlagParser):
    __pass_kwargs: bool = False

    matchers = {"keyword_argument": KEY_ARGUMENT}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.var_kwargs = {}

    def parse(self, *args):
        parsed = super().parse(*args)
        if self.__pass_kwargs:
            parsed["_kwargs"] = self.var_kwargs
        return parsed

    def handle_keyword_argument(self, argument: KeyArg):
        name = argument["name"].replace("-", "_")
        try:
            arg = self.get_or_raise(
                name,
                f"Argument {argument['name']}{config.arg_assignment}"
                f"{argument['value']} not recognized",
            )
            name = arg.name
            value = arg.convert(argument["value"])
        except errors.ParserError:
            if self.__pass_kwargs:
                value = argument["value"]
                self.var_kwargs[name] = value
                return None, None
            else:
                raise

        return name, value

    @classmethod
    def arg_hook(cls, param: Parameter, meta):
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

            cls.__pass_kwargs = True


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

    @classmethod
    def arg_hook(cls, param, meta):
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

            cls.__pass_args = True


class RawParser(ArgumentParser):
    def parse(self, cli_args):
        return {"_args": cli_args}

    @classmethod
    def arg_hook(cls, param, meta):
        if param.kind is not param.VAR_POSITIONAL:
            raise errors.CommandError(
                "Raw commands must only have a single *args argument"
            )


class ParsingMethod:
    STANDARD: Type[ArgumentParser] = StandardParser
    KEYWORD: Type[ArgumentParser] = KeywordParser
    POSITIONAL: Type[ArgumentParser] = PositionalParser
    RAW: Type[ArgumentParser] = RawParser
    FLAG: Type[ArgumentParser] = FlagParser
