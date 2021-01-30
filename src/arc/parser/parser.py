import re
from typing import List, Union, cast, Dict

from arc import config
from arc.errors import ParserError
from .data_types import COMMAND, FLAG, ARGUMENT
from . import data_types as types


class Tokenizer:
    TOKEN_TYPES = {
        COMMAND: fr"\A\b((?:\w+{config.utility_seperator})+\w+)\b",
        FLAG: fr"\A{config.flag_denoter}(?P<name>\b\w+)\b",
        ARGUMENT: fr"\A\b(?P<name>[a-zA-Z_]+\b){config.options_seperator}(?P<value>[\w\s\'\"-]+)\b",
    }

    def __init__(self, data: List[str]):
        self.data = data
        self.tokens: List[types.Token] = []

    def tokenize(self):
        while len(self.data) > 0:
            self.tokens.append(self.__tokenize_one_token())
        return self.tokens

    def __tokenize_one_token(self):
        for kind, pattern in self.TOKEN_TYPES.items():
            regex = re.compile(pattern)
            match_against = self.data[0].strip()
            if match := regex.match(match_against):
                value: Union[Dict[str, str], str]
                if groups := match.groupdict():
                    value = groups
                else:
                    value = match.group(1)

                # Checks if we match against the
                # entire string or just part of it
                # We probably don't need this anymore
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

        if self.peek() == COMMAND:
            return self.parse_command()

        raise ParserError("No Command Given")

    def parse_command(self):
        namespace = self.consume(COMMAND).split(":")
        return types.CommandNode(namespace, self.parse_body())

    def parse_body(self):
        args: List[types.KeywordNode] = []
        while self.peek() is not None:
            if self.peek() == FLAG:
                args.append(self.parse_flag())
            elif self.peek() == ARGUMENT:
                args.append(self.parse_option())

        return args

    def parse_option(self):
        argument = self.consume(ARGUMENT)
        argument = cast(Dict[str, str], argument)
        return types.KeywordNode(argument["name"], argument["value"], ARGUMENT)

    def parse_flag(self):
        flag = self.consume(FLAG)
        flag = cast(Dict[str, str], flag)
        return types.KeywordNode(flag["name"], "", FLAG)

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
