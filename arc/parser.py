import typing as t
from typing import TypedDict, Union
from dataclasses import dataclass
import re
import enum


from arc import errors, logging, utils
from arc.color import colorize, fg
from arc._command import helpers
from arc.context import Context
from arc.config import config
from arc.types.helpers import join_or
from arc.utils import IDENT, symbol
from arc._command.param import MISSING, Param

logger = logging.getArcLogger("parse")


class TokenType(enum.Enum):
    VALUE = 1
    KEYWORD = 2
    POS_ONLY = 3
    SHORT_KEYWORD = 4


# Note that this takes advantage of the fact that dictionaries
# are ordered.
matchers = {
    TokenType.KEYWORD: re.compile(fr"^{config.flag_prefix}({IDENT})$"),
    TokenType.SHORT_KEYWORD: re.compile(fr"^{config.short_flag_prefix}([a-zA-Z]+)$"),
    TokenType.POS_ONLY: re.compile(fr"^({config.flag_prefix})$"),
    TokenType.VALUE: re.compile(r"^(.+)$"),
}


@dataclass
class Token:
    value: str
    type: TokenType


class Parsed(TypedDict):
    pos_values: list[str]
    key_values: dict[str, Union[str, symbol]]


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
                    self.add_token(match, name)
                    break
            else:
                raise ValueError(f"Could not tokenize {curr}")

        return self.tokens

    def add_token(self, match: re.Match, kind: TokenType):
        value: str = match.groups()[0]
        self.tokens.append(Token(value, kind))


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

    def add_param(self, param: Param):
        self.params.append(param)
        if param.is_positional:
            self.pos_params.append(param)
        if param.is_keyword or param.is_flag:
            self._long_names[param.arg_alias] = param
            if param.short:
                self._short_names[param.short] = param

    def parse(self, args: list[str]):
        utils.header("PARSING")
        self.tokens = Lexer(args).tokenize()
        parser_table = {
            TokenType.KEYWORD: self.parse_keyword,
            TokenType.SHORT_KEYWORD: self.parse_short_keyword,
            TokenType.POS_ONLY: self.parse_pos_only,
            TokenType.VALUE: self.parse_value,
        }
        while self.tokens:
            curr = self.consume()
            if self.pos_only:
                if curr.type is TokenType.KEYWORD:
                    curr.value = f"{config.flag_prefix}{curr.value}"
                elif curr.type is TokenType.SHORT_KEYWORD:
                    curr.value = f"{config.short_flag_prefix}{curr.value}"
                self.parse_value(curr)
            else:
                parser_table[curr.type](curr)

        return self.parsed, self.extra

    def parse_keyword(self, token: Token):

        param = self._long_names.get(token.value)

        if not param:
            if self.allow_extra:
                self.extra.append(token.value)
                return
            else:
                raise self.non_existant_arg(token.value)

        if param.is_keyword and self.peek_type() == TokenType.VALUE:
            value = self.consume().value
        else:
            value = MISSING

        self.parsed[param.arg_name] = value

    def parse_short_keyword(self, token: Token):
        def process_single(char: str):
            param = self._short_names.get(char)
            if not param:
                if self.allow_extra:
                    self.extra.append(char)
                    return
                else:
                    raise self.non_existant_arg(token.value)

            if param.is_keyword and self.peek_type() == TokenType.VALUE:
                value = self.consume().value
            else:
                value = MISSING

            self.parsed[param.arg_name] = value

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
        self.parsed[param.arg_name] = token.value
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

    def non_existant_arg(self, val: str):
        styled = colorize(config.flag_prefix + val, fg.YELLOW)
        message = f"Option {styled} not recognized"

        suggest_args = [
            param.arg_alias for param in helpers.find_possible_params(self.params, val)
        ]

        if len(suggest_args) > 0:
            message += (
                f"\n\tPerhaps you meant {colorize(join_or(suggest_args), fg.YELLOW)}?"
            )

        return errors.UnrecognizedArgError(message, self.ctx)
