import re

from arc import Config
import arc.parser.data_types as types
from arc.errors import ParserError

# pylint: disable=missing-function-docstring, missing-class-docstring


class Tokenizer:
    def __init__(self, data):
        self.data = data
        self.TOKEN_TYPES = [
            ("flag", fr"{Config.flag_denoter}\b\w+\b"),
            ("option", fr"\b\w+{Config.options_seperator}[\"\'][\w\s\,\.]+\b[\"\']"),
            ("option", fr"\b\w+{Config.options_seperator}[\w\,\.]+\b"),
            ("utility", fr"\b\w+\b{Config.utility_seperator}"),
            ("script", r"\b\w+\b"),
        ]

    def tokenize(self):
        if len(self.data) == 0:
            raise ParserError("No provided input")

        tokens = []
        while len(self.data) > 0:
            tokens.append(self.__tokenize_one_token())
        return tokens

    def __tokenize_one_token(self):
        for name, regex in self.TOKEN_TYPES:
            regex = re.compile(fr"\A({regex})")
            if match := regex.match(self.data):
                value = match.group(1)
                self.data = self.data[match.end() :].strip()
                return types.Token(name, value)

        raise ParserError(f"Couldn't match token on {self.data}")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        if len(self.tokens) == 0:
            raise ParserError("No tokens to parse")

        return self.parse_util()

    def parse_util(self):
        if self.peek("utility"):
            util = self.consume("utility")
            return types.UtilNode(
                util.value.rstrip(Config.utility_seperator), self.parse_script()
            )

        return self.parse_script()

    def parse_script(self):
        if self.peek("script"):
            name = self.consume("script").value
        else:
            # for anonymous scripts
            name = Config.anon_identifier

        return types.ScriptNode(name, *self.parse_script_body())

    def parse_script_body(self):
        options = []
        flags = []
        for token in self.tokens.copy():
            if token.type == "option":
                options.append(self.parse_option(token))
            elif token.type == "flag":
                flags.append(self.parse_flag(token))
            else:
                raise ParserError(f"Invalid token '{token.type}' in script body")

        return options, flags

    def parse_option(self, token):
        self.consume("option")
        name, value = token.value.split(Config.options_seperator)
        return types.OptionNode(name, value)

    def parse_flag(self, token):
        self.consume("flag")
        return types.FlagNode(token.value.lstrip(Config.flag_denoter))

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


if __name__ == "__main__":
    t = Tokenizer("script value=2 --flag").tokenize()
    print(t)
    p = Parser(t).parse()
    print(p)
