import re
from typing import List
from dataclasses import dataclass

from arc import Config
from arc._utils import decorate_text
from arc.errors import ParserError

Config.debug = True
Config.log = True


@dataclass
class Token:
    type: str
    value: str


@dataclass
class OptionNode:
    name: str
    value: str

    def __repr__(self):
        return f"{self.name}={self.value}"


@dataclass
class FlagNode:
    name: str

    def __repr__(self):
        return self.name


@dataclass
class ScriptNode:
    name: str
    options: List[OptionNode]
    flags: List[FlagNode]

    def __repr__(self, level=0):
        tabs = "\t" * level
        string = (
            f"{decorate_text('SCRIPT', tcolor='33')}\n{tabs}"
            f"name: {decorate_text(self.name, tcolor='32')}"
            f"\n{tabs}options: {', '.join([decorate_text(str(o)) for o in self.options])}"
            f"\n{tabs}flags: {', '.join([decorate_text(str(f)) for f in self.flags])}"
        )
        return string


@dataclass
class UtilNode:
    name: str
    script: ScriptNode

    def __repr__(self):
        string = (
            f"{decorate_text('UTILITY', tcolor='33')}\n"
            f"name: {decorate_text(self.name, tcolor='32')}"
            f"\nscript: \n\t{self.script.__repr__(level=1)}"
        )
        return string


class Tokenizer:
    TOKEN_TYPES = [
        ("flag", fr"{Config.flag_denoter}\b[a-zA-Z_0-9]*\b"),
        ("option", fr"\b[a-zA-Z_0-9]*{Config.options_seperator}[a-zA-Z_0-9]*\b"),
        ("utility", fr"\b[a-zA-Z_0-9]*{Config.utility_seperator}"),
        ("script", r"\b[a-zA-Z_0-9]*\b"),
    ]

    def __init__(self, data):
        self.data = data

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
                return Token(name, value)

        raise ParserError(f"Couldn't match token on {self.data}")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        if len(self.tokens) == 0:
            raise ParserError("No tokens to parse")

        return self.parse_util()

    def parse_util(self):
        try:
            util = self.consume("utility")
            return UtilNode(util.value.rstrip(":"), self.parse_script())
        except ParserError:
            return self.parse_script()

    def parse_script(self):
        script = self.consume("script")

        options = filter(lambda o: o.type == "option", self.tokens)
        flags = filter(lambda f: f.type == "flag", self.tokens)

        return ScriptNode(
            script.value, self.parse_options(options), self.parse_flags(flags)
        )

    def parse_options(self, tokens):
        parsed_options = []
        for option in tokens:
            name, value = option.value.split("=")
            parsed_options.append(OptionNode(name, value))

        return parsed_options

    def parse_flags(self, tokens):
        parsed_flags = []
        for flag in tokens:
            parsed_flags.append(FlagNode(flag.value.lstrip(Config.flag_denoter)))

        return parsed_flags

    def consume(self, expected_type):
        if (actual_type := self.tokens[0].type) == expected_type:
            return self.tokens.pop(0)

        raise ParserError(
            "Unexpected token.",
            f"Expected token type '{expected_type}', got '{actual_type}'",
        )

