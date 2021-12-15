import typing as t
import sys
import shlex
from typing import TypedDict, Union
from dataclasses import dataclass
import re
import enum

from arc.context import AppContext
from arc import errors, logging
from arc.config import config
from arc.utils import IDENT
from arc.utils import symbol
from arc.command.param import MISSING, Param

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

    def __init__(self, ctx: AppContext, allow_extra: bool = False):
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
                self.parse_value(curr)
            else:
                parser_table[curr.type](curr)

        return self.parsed, self.extra

    def parse_keyword(self, token: Token):
        if (next_token := self.peek()) and next_token.type == TokenType.VALUE:
            value = self.consume().value
        else:
            value = MISSING

        param = self._long_names.get(token.value)

        if not param:
            if self.allow_extra:
                self.extra.extend([token.value, value])
            else:
                raise errors.ParserError(f"Unrecognized keyword: {token.value}")
        else:
            self.parsed[param.arg_name] = value

    def parse_short_keyword(self, token: Token):
        def process_single(char: str, flag: bool = False):
            if flag:
                value = MISSING
            elif (next_token := self.peek()) and next_token.type == TokenType.VALUE:
                value = self.consume().value
            else:
                value = MISSING

            param = self._short_names.get(char)
            if not param:
                if self.allow_extra:
                    extra = [char]
                    if value is not MISSING:
                        extra.append(value)  # type: ignore

                    self.extra.extend(extra)
                else:
                    raise errors.ParserError(f"Unrecognized keyword: {char}")
            else:
                self.parsed[param.arg_name] = value

        if len(token.value) > 1:
            # Flags, cannot recieve a value
            for char in token.value:
                process_single(char, flag=True)
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
                raise errors.ParserError("Too many positional arguments")

        param = self.pos_params[self.curr_pos]
        self.parsed[param.arg_name] = token.value
        self.curr_pos += 1

    def consume(self):
        return self.tokens.pop(0)

    def peek(self):
        return self.tokens[0] if self.tokens else None
