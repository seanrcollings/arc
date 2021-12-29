import typing as t
from typing import TypedDict, Union
from dataclasses import dataclass
import re
import enum


from arc import errors, logging, utils, constants
from arc.color import colorize, fg
from arc._command import helpers
from arc.context import Context
from arc.types.helpers import join_or
from arc.utils import IDENT
from arc._command.param import Param, ParamAction

logger = logging.getArcLogger("parse")


class TokenType(enum.Enum):
    VALUE = 1
    KEYWORD = 2
    POS_ONLY = 3
    SHORT_KEYWORD = 4


# Note that this takes advantage of the fact that dictionaries
# are ordered.
matchers = {
    TokenType.KEYWORD: re.compile(fr"^{constants.FLAG_PREFIX}({IDENT})$"),
    TokenType.SHORT_KEYWORD: re.compile(fr"^{constants.SHORT_FLAG_PREFIX}([a-zA-Z]+)$"),
    TokenType.POS_ONLY: re.compile(fr"^({constants.FLAG_PREFIX})$"),
    TokenType.VALUE: re.compile(r"^(.+)$"),
}


@dataclass
class Token:
    value: str
    type: TokenType
    raw: str


class Lexer:
    def __init__(self, args: list[str]):
        self.args = args
        self.tokens: list[Token] = []

    def tokenize(self):
        while self.args:
            curr: str = self.args.pop(0)
            for name, regex in matchers.items():
                if match := regex.match(curr):
                    logger.debug("Matched %s -> %s", curr, name)
                    self.add_token(curr, match, name)
                    break
            else:
                raise ValueError(f"Could not tokenize {curr}")

        return self.tokens

    def add_token(self, string: str, match: re.Match, kind: TokenType):
        value: str = match.groups()[0]
        self.tokens.append(Token(value, kind, string))


class Parser:
    tokens: list[Token]

    def __init__(self, ctx: Context, allow_extra: bool = False):
        self.ctx = ctx
        self.allow_extra = allow_extra
        self.parsed: dict[str, t.Any] = {}
        self.extra: list[str] = []
        self.pos_only = False
        self.params: list[Param] = []
        self.pos_params: list[Param] = []
        self.curr_pos: int = 0
        self._long_names: dict[str, Param] = {}
        self._short_names: dict[str, Param] = {}
        self.parser_table = {
            TokenType.KEYWORD: self.parse_keyword,
            TokenType.SHORT_KEYWORD: self.parse_short_keyword,
            TokenType.POS_ONLY: self.parse_pos_only,
            TokenType.VALUE: self.parse_value,
        }

    def add_param(self, param: Param):
        self.params.append(param)
        if param.is_positional:
            self.pos_params.append(param)
        if param.is_keyword or param.is_flag:
            self._long_names[param.arg_alias] = param
            if param.short:
                self._short_names[param.short] = param

    def handle_value(self, param: Param, value: str):
        if param.action is ParamAction.STORE:
            self.parsed[param.arg_name] = value
        elif param.action is ParamAction.APPEND:
            if value is not constants.MISSING:
                self.parsed.setdefault(param.arg_name, []).append(value)
        elif param.action is ParamAction.COUNT:
            if param.arg_name not in self.parsed:
                self.parsed[param.arg_name] = 0

            self.parsed[param.arg_name] += 1

    def parse(self, args: list[str]):
        utils.header("PARSING")
        self.tokens = Lexer(args).tokenize()

        while self.tokens:
            curr = self.consume()
            self.handle_token(curr)

        return self.parsed, self.extra

    def handle_token(self, token: Token):
        if self.pos_only:
            token.value = token.raw
            self.parse_value(token)
        else:
            self.parser_table[token.type](token)

    def parse_keyword(self, token: Token):
        param = self._long_names.get(token.value)

        if not param:
            if self.allow_extra:
                self.extra.append(constants.FLAG_PREFIX + token.value)
                return
            else:
                raise self.non_existant_arg(token)

        if param.is_keyword and self.peek_type() == TokenType.VALUE:
            value = self.consume().value
        else:
            value = constants.MISSING

        self.handle_value(param, value)

    def parse_short_keyword(self, token: Token):
        def process_single(char: str):
            param = self._short_names.get(char)
            if not param:
                if self.allow_extra:
                    self.extra.append(constants.SHORT_FLAG_PREFIX + char)
                    return
                else:
                    raise self.non_existant_arg(token)

            if param.is_keyword and self.peek_type() == TokenType.VALUE:
                value = self.consume().value
            else:
                value = constants.MISSING

            self.handle_value(param, value)

        if len(token.value) > 1:
            # Flags, cannot recieve a value
            for char in token.value:
                process_single(char)
        else:
            # May recieve a value
            process_single(token.value)

    def parse_pos_only(self, _token: Token):
        self.pos_only = True

    def parse_value(self, token: Token):
        if len(self.pos_params) <= self.curr_pos:
            if self.allow_extra:
                self.extra.append(token.value)
                return
            else:
                raise errors.UnrecognizedArgError(
                    "Too many positional arguments", self.ctx
                )

        param = self.pos_params[self.curr_pos]
        self.handle_value(param, token.value)
        if param.action is ParamAction.APPEND:
            if len(self.parsed[param.arg_name]) == param.nargs:
                self.curr_pos += 1
        else:
            self.curr_pos += 1

    def consume(self):
        return self.tokens.pop(0)

    def peek(self):
        return self.tokens[0] if self.tokens else None

    def peek_type(self) -> t.Optional[TokenType]:
        next_token = self.peek()
        if next_token:
            return next_token.type
        return None

    def non_existant_arg(self, token: Token):
        styled = colorize(token.raw, fg.YELLOW)
        message = f"Option {styled} not recognized"

        if self.ctx.suggestions["suggest_arguments"]:
            suggest_args = [
                param.arg_alias
                for param in helpers.find_possible_params(
                    self.params,
                    token.value,
                    self.ctx.suggestions["levenshtein_distance"],
                )
            ]

            if len(suggest_args) > 0:
                message += (
                    f"\nPerhaps you meant {colorize(join_or(suggest_args), fg.YELLOW)}?"
                )

        return errors.UnrecognizedArgError(message, self.ctx)


class CLIOptionsParser(Parser):
    """Parser sub class used for global CLI options
    to that the inital CLI parse doesn't eat things like
    comand-specific `--help`.
    The first time we encounter a `TokenType.VALUE` to parse, the parser
    will exit with all additional data in `extra`
    """

    class CommandNameEncountered(errors.ArcError):
        ...

    def parse(self, args: list[str]):
        try:
            return super().parse(args)
        except CLIOptionsParser.CommandNameEncountered:
            return self.parsed, self.extra

    def parse_value(self, token: Token):
        self.extra = [token.value] + [token.raw for token in self.tokens]
        raise CLIOptionsParser.CommandNameEncountered()
