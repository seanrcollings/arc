import re
from typing import List, Union, cast, Dict
import shlex

from arc import arc_config
from arc.errors import ParserError, TokenizerError
from arc import utils
from .data_types import (
    COMMAND,
    FLAG,
    POS_ARGUMENT,
    KEY_ARGUMENT,
    TokenizerMode,
)
from . import data_types as types

IDENT = r"[a-zA-Z-_0-9]+"


class Tokenizer:
    """
    Arc Tokenizer class

    :param data: List of strings to parse. Can split a normal string with shlex.split()

    ### Attributes
    data: Data to be parsed
    tokens: List of Tokens
    """

    TOKEN_TYPES = {
        TokenizerMode.COMMAND: {
            COMMAND: fr"\A\b((?:(?:{IDENT}:)+{IDENT})|{IDENT}:?)$",
        },
        TokenizerMode.BODY: {
            FLAG: fr"\A{arc_config.flag_denoter}(?P<name>\b{IDENT})$",
            KEY_ARGUMENT: fr"\A\b(?P<name>{IDENT}\b){arc_config.arg_assignment}(?P<value>.+)$",
            POS_ARGUMENT: r"\A(.+)$",
        },
    }

    def __init__(self, data: List[str]):
        self.data = data
        self.tokens: List[types.Token] = []
        self.mode = TokenizerMode.COMMAND

    def tokenize(self):
        while len(self.data) > 0:
            if token := self.__tokenize_one_token():
                if token is not None:
                    self.tokens.append(token)
        return self.tokens

    def __tokenize_one_token(self):
        for kind, pattern in self.TOKEN_TYPES[self.mode].items():
            regex = re.compile(pattern)
            match_against = self.data[0]
            # empty tokens are ignored
            if match_against == "":
                self.data.pop(0)
                return None

            if match := regex.match(match_against):
                value = self.__get_value(match)

                if len(match_against) == match.end():
                    self.data.pop(0)
                    if self.mode == TokenizerMode.COMMAND:
                        self.mode = TokenizerMode.BODY
                    return types.Token(kind, value)

        if self.mode == TokenizerMode.COMMAND:
            self.mode = TokenizerMode.BODY
        else:
            # we only want to raise an error if we're in the body
            # mode because at some point we may need to parse
            # something without a command
            raise TokenizerError(self.data[0], self.mode)

    @staticmethod
    def __get_value(match: re.Match) -> Union[Dict[str, str], str]:
        if groups := match.groupdict():
            return groups

        return match.group(1)


class Parser:
    def __init__(self, tokens):
        self.tokens: List[types.Token] = tokens

    def parse(self):
        return self.parse_command()
        # if self.peek() is COMMAND:

        # raise ParserError("No Command Given")

    def parse_command(self):
        namespace = []
        if self.peek() is COMMAND:
            namespace = [
                n.replace("-", "_") for n in cast(str, self.consume(COMMAND)).split(":")
            ]

        return types.CommandNode(namespace, self.parse_body())

    def parse_body(self):
        args: List[types.ArgNode] = []
        while self.peek() is not None:
            token = self.peek()
            if token is FLAG:
                args.append(self.parse_flag())
            elif token is KEY_ARGUMENT:
                args.append(self.parse_option())
            elif token is POS_ARGUMENT:
                arg = cast(str, self.consume(POS_ARGUMENT))
                args.append(types.ArgNode(None, arg, POS_ARGUMENT))

        return args

    def parse_option(self):
        argument = self.consume(KEY_ARGUMENT)
        argument = cast(Dict[str, str], argument)
        return types.ArgNode(
            argument["name"].replace("-", "_"), argument["value"], KEY_ARGUMENT
        )

    def parse_flag(self):
        flag = self.consume(FLAG)
        flag = cast(Dict[str, str], flag)
        return types.ArgNode(flag["name"].replace("-", "_"), "", FLAG)

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


@utils.timer("Parsing")
def parse(command: Union[List[str], str], handle=True) -> types.CommandNode:
    """Convenience wrapper around the
    tokenizer and parser.

    :param command: string or list of strings to be parsed.
    If it's a string, it will be split using shlex.split
    """
    if isinstance(command, str):
        command = shlex.split(command)

    with utils.handle(TokenizerError, ParserError, handle=handle):
        tokens = Tokenizer(command).tokenize()
        parsed = Parser(tokens).parse()
    return parsed
