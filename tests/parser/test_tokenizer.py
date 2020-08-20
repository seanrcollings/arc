from tests.base_test import BaseTest
from arc.parser import Tokenizer
from arc.parser.data_types import Token
from arc.errors import ParserError

# pylint: disable=protected-access, missing-function-docstring
class TestTokenizer(BaseTest):
    def test_no_input(self):
        with self.assertRaises(ParserError):
            Tokenizer("").tokenize()

    def test_tokenize(self):
        """'Test basic tokenizing behavior"""
        tokens = Tokenizer(
            ["util:script", "option=value", "option=value", "--flag"]
        ).tokenize()
        test_tokens = [
            Token("utility", "util:"),
            Token("script", "script"),
            Token("option", "option=value"),
            Token("option", "option=value"),
            Token("flag", "--flag"),
        ]
        self.assertEqual(tokens, test_tokens)

        tokens = Tokenizer(
            ["util:script", "option=value", "--flag", "option=value"]
        ).tokenize()
        test_tokens = [
            Token("utility", "util:"),
            Token("script", "script"),
            Token("option", "option=value"),
            Token("flag", "--flag"),
            Token("option", "option=value"),
        ]

        self.assertEqual(tokens, test_tokens)

    def test_tokenize_options(self):
        tokens = Tokenizer(
            ["option=value", "option2=value2,value2", "option3=value with spaces"]
        ).tokenize()
        test_tokens = [
            Token("option", "option=value"),
            Token("option", "option2=value2,value2"),
            Token("option", "option3=value with spaces"),
        ]
        self.assertEqual(tokens, test_tokens)
