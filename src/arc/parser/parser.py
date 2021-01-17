import re
from enum import Enum
from typing import List

from arc import config
import arc.parser.data_types as types
from arc.errors import ParserError

# Parser Enhancement Project
# Token Types
#   - Operator (--, =, :)
#   - Identifier (any string of text, seperated by an operator or whitespace)


class Operator(Enum):
    utility = config.utility_seperator
    options = config.options_seperator
    flag = config.flag_denoter

    @classmethod
    def get(cls, string):
        for item in cls:
            if item.value == string:
                return item
        raise ValueError(f"{string} is not a valid operator")


class Tokenizer:
    TOKEN_TYPES = {
        "operator": fr"({config.flag_denoter}|{config.options_seperator}|"
        fr"{config.utility_seperator})",
        "identifier": r"\b\w+\b",
    }

    def __init__(self, data: List[str]):
        self.data = data

    def tokenize(self):
        tokens = []
        while len(self.data) > 0:
            tokens.append(self.__tokenize_one_token())
        return tokens

    def __tokenize_one_token(self):
        for kind, pattern in self.TOKEN_TYPES.items():
            regex = re.compile(fr"\A({pattern})")
            match_against = self.data[0].strip()
            if match := regex.match(match_against):
                value = match.group(1)
                # Checks if we match against the
                # entire string or just part of it
                if len(match_against) == match.end():
                    self.data.pop(0)
                else:
                    self.data[0] = self.data[0][match.end() :].strip()

                if kind == "operator":
                    return types.Token(kind, Operator.get(value))
                return types.Token(kind, value)

        raise ParserError(f"Couldn't match token on {self.data[0]}")


class Parser:
    def __init__(self, tokens):
        self.tokens: List[types.Token] = tokens

    def parse(self):
        return self.parse_util()

    def parse_util(self):
        if self.peek("utility"):
            util = self.consume("utility")
            return types.UtilNode(
                util.value.rstrip(config.utility_seperator), self.parse_script()
            )

        return self.parse_script()

    def parse_script(self):
        if self.peek("script"):
            name = self.consume("script").value
        else:
            # for anonymous scripts
            name = config.anon_identifier

        return types.ScriptNode(name, *self.parse_script_body())

    def parse_script_body(self):
        options = []
        flags = []
        args = []

        for token in self.tokens.copy():
            if token.type == "option":
                options.append(self.parse_option(token))
            elif token.type == "flag":
                flags.append(self.parse_flag(token))
            else:
                args.append(self.parse_arg(token))

        return options, flags, args

    def parse_option(self, token):
        self.consume("option")
        name, value = token.value.split(config.options_seperator)
        return types.OptionNode(name, value)

    def parse_flag(self, token):
        self.consume("flag")
        return types.FlagNode(token.value.lstrip(config.flag_denoter))

    def parse_arg(self, token):
        self.consume(self.tokens[0].type)
        return types.ArgNode(token.value)

    def consume(self, expected_type):
        if len(self.tokens) == 0:
            raise ParserError("No tokens to consume")

        if (actual_type := self.tokens[0].type) == expected_type:
            return self.tokens.pop(0)

        raise ParserError(
            "Unexpected token.",
            f"Expected token type '{expected_type}', got '{actual_type}'",
        )

    def peek(self, expected_type):
        try:
            return expected_type == self.tokens[0].type
        except IndexError:
            return False
