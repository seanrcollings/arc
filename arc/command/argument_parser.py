import logging
from typing import TypedDict, Union
from dataclasses import dataclass
import re
import enum
from arc.config import config
from arc.utils import IDENT
from arc.types.params import MISSING
from arc.utils.other import symbol


logger = logging.getLogger("arc_logger")


class TokenType(enum.Enum):
    VALUE = 1
    KEYWORD = 2
    POS_ONLY = 3
    SHORT_KEYWORD = 4


matchers = {
    TokenType.KEYWORD: re.compile(fr"^{config.flag_denoter}({IDENT})$"),
    TokenType.SHORT_KEYWORD: re.compile(fr"^{config.short_flag_denoter}([a-zA-Z]+)$"),
    TokenType.POS_ONLY: re.compile(fr"^({config.flag_denoter})$"),
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
    def __init__(self, to_tokenize: list[str]):
        self.to_tokenize = to_tokenize
        self.tokens: list[Token] = []

    def tokenize(self):
        while len(self.to_tokenize) > 0:
            curr: str = self.to_tokenize.pop(0)
            for name, regex in matchers.items():
                if match := regex.match(curr):
                    logger.debug(f"Matched {curr} -> {name}")
                    self.add_token(match, name)
                    break
            else:
                raise ValueError(f"Could not tokenize {curr}")

        return self.tokens

    def add_token(self, match: re.Match, kind: TokenType):
        value: str = match.groups()[0]
        self.tokens.append(Token(value, kind))


class ArgumentParser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.parsed: Parsed = {"pos_values": [], "key_values": {}}
        self.pos_only = False

    def parse(self):
        parser_table = {
            TokenType.KEYWORD: self.parse_keyword,
            TokenType.SHORT_KEYWORD: self.parse_short_keyword,
            TokenType.POS_ONLY: self.parse_pos_only,
            TokenType.VALUE: self.parse_value,
        }
        while self.tokens:
            curr = self.consume()
            if self.pos_only and curr.type != TokenType.VALUE:
                raise ValueError("POS ONLY")
            parser_table[curr.type](curr)

        return self.parsed

    def parse_keyword(self, token: Token):
        if (next_token := self.peek()) and next_token.type == TokenType.VALUE:
            value = self.consume().value
        else:
            value = MISSING

        self.parsed["key_values"][token.value] = value

    def parse_short_keyword(self, token: Token):
        if (next_token := self.peek()) and next_token.type == TokenType.VALUE:
            assert len(token.value) == 1
            self.parsed["key_values"][token.value] = self.consume().value
        else:
            for char in token.value:
                self.parsed["key_values"][char] = MISSING

    def parse_pos_only(self, _token: Token):
        self.pos_only = True

    def parse_value(self, token: Token):
        self.parsed["pos_values"].append(token.value)

    def consume(self):
        return self.tokens.pop(0)

    def peek(self):
        return self.tokens[0] if self.tokens else None


def parse(args: list[str]):
    tokens = Lexer(args).tokenize()
    return ArgumentParser(tokens).parse()


if __name__ == "__main__":
    lexer = Lexer(
        [
            "--name",
            "value",
            "--name2",
            "value2",
            "--flag",
            "-f",
            "-vb",
            "--",
            "other such things and stuff",
        ]
    )
    parser = ArgumentParser(lexer.tokenize())
    print(parser.parse())
