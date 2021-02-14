from unittest import TestCase
from arc.parser import Tokenizer
from arc.parser.data_types import Token, COMMAND, KEY_ARGUMENT, FLAG, POS_ARGUMENT


class TestTokenizer(TestCase):
    def test_tokenize(self):
        """'Test basic tokenizing behavior"""
        tokens = Tokenizer(
            ["util:command", "option=value", "option2=value", "--flag"]
        ).tokenize()
        test_tokens = [
            Token(COMMAND, "util:command"),
            Token(KEY_ARGUMENT, {"name": "option", "value": "value"}),
            Token(KEY_ARGUMENT, {"name": "option2", "value": "value"}),
            Token(FLAG, {"name": "flag"}),
        ]
        self.assertEqual(tokens, test_tokens)

        tokens = Tokenizer(
            [
                "util:command",
                "option1=value",
                "--flag",
                "option=value",
                "value",
                "value,with,commas",
            ]
        ).tokenize()
        test_tokens = [
            Token(COMMAND, "util:command"),
            Token(KEY_ARGUMENT, {"name": "option1", "value": "value"}),
            Token(FLAG, {"name": "flag"}),
            Token(KEY_ARGUMENT, {"name": "option", "value": "value"}),
            Token(POS_ARGUMENT, "value"),
            Token(POS_ARGUMENT, "value,with,commas"),
        ]

        self.assertEqual(tokens, test_tokens)

    def test_tokenize_options(self):
        tokens = Tokenizer(
            [
                "command",
                "option1=value",
                "option_two=value1,value2",
                "option_three=thing with spaces",
            ]
        ).tokenize()
        test_tokens = [
            Token(COMMAND, "command"),
            Token(KEY_ARGUMENT, {"name": "option1", "value": "value"}),
            Token(KEY_ARGUMENT, {"name": "option_two", "value": "value1,value2"}),
            Token(KEY_ARGUMENT, {"name": "option_three", "value": "thing with spaces"}),
        ]
        self.assertEqual(tokens, test_tokens)
