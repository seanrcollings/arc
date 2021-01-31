import re
from typing import List, Union, cast, Dict
import shlex

from arc import config
from arc.errors import ParserError
from arc import utils
from .data_types import COMMAND, FLAG, ARGUMENT, POS_ARGUMENT, KEY_ARGUMENT
from . import data_types as types


class Tokenizer:
    TOKEN_TYPES = {
        FLAG: fr"\A{config.flag_denoter}(?P<name>\b\w+)\b",
        ARGUMENT: fr"\A\b(?P<name>[a-zA-Z_]+\b){config.options_seperator}(?P<value>[\w\s\-\,\._]+)\b",
        COMMAND: r"\A\b((?:(?:\w+:)+\w+)|\w+)\b",
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

                if len(match_against) == match.end():
                    self.data.pop(0)
                    return types.Token(kind, value)

        raise ParserError(f"Couldn't match token on {self.data[0]}")


class Parser:
    def __init__(self, tokens):
        self.tokens: List[types.Token] = tokens

    def parse(self):
        if len(self.tokens) == 0:
            raise ParserError("No tokens provided to parse")

        if self.peek() is COMMAND:
            return self.parse_command()

        raise ParserError("No Command Given")

    def parse_command(self):
        namespace = self.consume(COMMAND).split(":")
        return types.CommandNode(namespace, self.parse_body())

    def parse_body(self):
        args: List[types.ArgNode] = []
        while self.peek() is not None:
            if self.peek() is FLAG:
                args.append(self.parse_flag())
            elif self.peek() is ARGUMENT:
                args.append(self.parse_option())
            elif self.peek() is COMMAND:
                # Hack for positional args.
                # Think of a better way to handle this
                args.append(types.ArgNode(None, self.consume(COMMAND), POS_ARGUMENT))

        return args

    def parse_option(self):
        argument = self.consume(ARGUMENT)
        argument = cast(Dict[str, str], argument)
        return types.ArgNode(argument["name"], argument["value"], KEY_ARGUMENT)

    def parse_flag(self):
        flag = self.consume(FLAG)
        flag = cast(Dict[str, str], flag)
        return types.ArgNode(flag["name"], "", FLAG)

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


def parse(command: Union[List[str], str]):
    """Convenience wrapper around the
    tokenizer and parser.

    :param command: string or list of strings to be parsed.
    If it's a string, it will be split using shlex.split
    """
    if isinstance(command, str):
        command = shlex.split(command)

    tokens = Tokenizer(command).tokenize()
    with utils.HandleException():
        parsed = Parser(tokens).parse()
    return parsed
