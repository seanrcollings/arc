import re

from arc import Config
import arc.parser.data_classes as dc
from arc.errors import ParserError

# pylint: disable=missing-function-docstring


class Tokenizer:
    def __init__(self, data):
        self.data = data
        self.TOKEN_TYPES = [
            ("flag", fr"{Config.flag_denoter}\b\w+\b"),
            ("option", fr"\b\w+{Config.options_seperator}[\"\']?\w+\b[\"\']?"),
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

                return dc.Token(name, value)

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
            return dc.UtilNode(
                util.value.rstrip(Config.utility_seperator), self.parse_script()
            )

        return self.parse_script()

    def parse_script(self):
        if self.peek("script"):
            script = self.consume("script")
            return dc.ScriptNode(script.value, *self.parse_script_body())

        # for anonymous scripts
        return dc.ScriptNode(Config.anon_identifier, *self.parse_script_body())

    def parse_script_body(self):
        options = filter(lambda o: o.type == "option", self.tokens)
        flags = filter(lambda f: f.type == "flag", self.tokens)
        return self.parse_options(options), self.parse_flags(flags)

    @staticmethod
    def parse_options(tokens):
        parsed_options = []
        for option in tokens:
            name, value = option.value.split("=")
            parsed_options.append(dc.OptionNode(name, value))

        return parsed_options

    @staticmethod
    def parse_flags(tokens):
        parsed_flags = []
        for flag in tokens:
            parsed_flags.append(dc.FlagNode(flag.value.lstrip(Config.flag_denoter)))

        return parsed_flags

    def consume(self, expected_type):
        if (actual_type := self.tokens[0].type) == expected_type:
            return self.tokens.pop(0)

        raise ParserError(
            "Unexpected token.",
            f"Expected token type '{expected_type}', got '{actual_type}'",
        )

    def peek(self, expected_type):
        return expected_type == self.tokens[0].type
