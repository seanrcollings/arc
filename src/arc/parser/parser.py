import re
from enum import Enum
from typing import List, Union

from arc import config
import arc.parser.data_types as types
from arc.errors import ParserError


IDENTIFIER = "identifier"
OPERATOR = "operator"


class Tokenizer:
    TOKEN_TYPES = {
        OPERATOR: fr"({config.flag_denoter}|{config.options_seperator}|"
        fr"{config.utility_seperator})",
        IDENTIFIER: r"\b[\w\,\.\s\\\/-]+\b",
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

                return types.Token(kind, value)

        raise ParserError(f"Couldn't match token on {self.data[0]}")


class Parser:
    def __init__(self, tokens):
        self.tokens: List[types.Token] = tokens

    def parse(self):
        if len(self.tokens) == 0:
            raise ParserError("No tokens provided to parse")

        if self.peek(1) == OPERATOR:
            return self.parse_util()
        return self.parse_script()

    def parse_util(self):
        util_name = self.consume(IDENTIFIER)
        self.consume(OPERATOR)
        return types.UtilNode(util_name, self.parse_script())

    def parse_script(self):
        script_name = self.consume(IDENTIFIER)
        return types.ScriptNode(script_name, self.parse_body())

    def parse_body(self):
        args: List[Union[types.KeywordNode, types.ArgNode]] = []
        while self.peek() is not None:
            if self.peek(1) == OPERATOR:
                args.append(self.parse_option())
            elif self.peek() == OPERATOR:
                args.append(self.parse_flag())
            else:
                args.append(self.parse_arg())

        return args

    def parse_option(self):
        name = self.consume(IDENTIFIER)
        self.consume(OPERATOR)
        value = self.consume(IDENTIFIER)
        return types.KeywordNode(name, value)

    def parse_flag(self):
        self.consume(OPERATOR)
        name = self.consume(IDENTIFIER)
        return types.KeywordNode(name, "true")

    def parse_arg(self):
        return types.ArgNode(self.consume("identifier"))

    def consume(self, expected_type):
        token_type = self.tokens[0].type
        if token_type == expected_type:
            return self.tokens.pop(0).value
        raise ValueError(
            f"Expected token of type: {expected_type}, got: {self.tokens[0].type}"
        )

    def peek(self, idx: int = 0):
        try:
            return self.tokens[idx].type
        except IndexError:
            return None
