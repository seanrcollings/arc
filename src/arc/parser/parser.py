import re
from typing import List, Union

from arc import config
import arc.parser.data_types as types
from arc.errors import ParserError
from arc.color import fg, bg, effects


COMMAND = "command"
FLAG = "flag"
ARGUMENT = "argument"


class Tokenizer:
    TOKEN_TYPES = {
        COMMAND: fr"\A\b((?:\w+{config.utility_seperator})+\w+)\b",
        FLAG: fr"\A({config.flag_denoter}\b\w+)\b",
        ARGUMENT: fr"\A\b(?P<name>[a-zA-Z_]+\b){config.options_seperator}(?P<value>[\w\s\'\"-]+)\b",
    }

    def __init__(self, data: List[str]):
        self.data = data
        self.tokens: List[types.Token] = []

    def __str__(self):
        token_color_map = {
            COMMAND: bg.GREEN,
            FLAG: bg.YELLOW,
            ARGUMENT: bg.BLUE,
        }

        # Argument Tokens value is a dict,
        # while others are just a string
        fmt_value = (
            lambda value: value
            if isinstance(value, str)
            else f"{value['name']}{config.options_seperator}{value['value']}"
        )

        colored = " ".join(
            f"{fg.BLACK}{token_color_map[token.type]}"
            f" {fmt_value(token.value)} {effects.CLEAR}"
            for token in self.tokens
        )

        key = (
            f"COMMAND: {token_color_map[COMMAND]}  {effects.CLEAR} "
            f"ARGUMENT: {token_color_map[ARGUMENT]}  {effects.CLEAR}"
            f" FLAG: {token_color_map[FLAG]}  {effects.CLEAR} "
        )

        return f"{colored}\n\n{key}"

    def tokenize(self):
        while len(self.data) > 0:
            self.tokens.append(self.__tokenize_one_token())
        return self.tokens

    def __tokenize_one_token(self):
        for kind, pattern in self.TOKEN_TYPES.items():
            regex = re.compile(pattern)
            match_against = self.data[0].strip()
            if match := regex.match(match_against):
                if groups := match.groupdict():
                    value = groups
                else:
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
        name = self.consume(ARGUMENT)
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
