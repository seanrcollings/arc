from tests.base_test import BaseTest
from arc.parser import Tokenizer
from arc.parser.data_types import Token, COMMAND, ARGUMENT, FLAG


class TestTokenizer(BaseTest):
    def test_tokenize(self):
        """'Test basic tokenizing behavior"""
        tokens = Tokenizer(
            ["util:script", "option=value", "option=value", "--flag"]
        ).tokenize()
        test_tokens = [
            Token(COMMAND, "util:script"),
            Token(ARGUMENT, {"name": "option", "value": "value"}),
            Token(ARGUMENT, {"name": "option", "value": "value"}),
            Token(FLAG, {"name": "flag"}),
        ]
        self.assertEqual(tokens, test_tokens)

        tokens = Tokenizer(
            ["util:script", "option=value", "--flag", "option=value"]
        ).tokenize()
        test_tokens = [
            Token(COMMAND, "util:script"),
            Token(ARGUMENT, {"name": "option", "value": "value"}),
            Token(FLAG, {"name": "flag"}),
            Token(ARGUMENT, {"name": "option", "value": "value"}),
        ]

        self.assertEqual(tokens, test_tokens)

    def test_tokenize_options(self):
        tokens = Tokenizer(
            [
                "option=value",
                "option_two=value1,value2",
                "option_three=thing with spaces",
            ]
        ).tokenize()
        test_tokens = [
            Token(ARGUMENT, {"name": "option", "value": "value"}),
            Token(ARGUMENT, {"name": "option_two", "value": "value1,value2"}),
            Token(ARGUMENT, {"name": "option_three", "value": "thing with spaces"}),
        ]
        self.assertEqual(tokens, test_tokens)
