from tests.base_test import BaseTest
from arc.parser import Tokenizer
from arc.parser.data_types import Token


class TestTokenizer(BaseTest):
    def test_tokenize(self):
        """'Test basic tokenizing behavior"""
        tokens = Tokenizer(
            ["util:script", "option=value", "option=value", "--flag"]
        ).tokenize()
        test_tokens = [
            Token("identifier", "util"),
            Token("operator", ":"),
            Token("identifier", "script"),
            Token("identifier", "option"),
            Token("operator", "="),
            Token("identifier", "value"),
            Token("identifier", "option"),
            Token("operator", "="),
            Token("identifier", "value"),
            Token("operator", "--"),
            Token("identifier", "flag"),
        ]
        self.assertEqual(tokens, test_tokens)

        tokens = Tokenizer(
            ["util:script", "option=value", "--flag", "option=value"]
        ).tokenize()
        test_tokens = [
            Token("identifier", "util"),
            Token("operator", ":"),
            Token("identifier", "script"),
            Token("identifier", "option"),
            Token("operator", "="),
            Token("identifier", "value"),
            Token("operator", "--"),
            Token("identifier", "flag"),
            Token("identifier", "option"),
            Token("operator", "="),
            Token("identifier", "value"),
        ]

        self.assertEqual(tokens, test_tokens)

    def test_tokenize_options(self):
        tokens = Tokenizer(
            ["option=value", "option2=value2,value2", "option3=value with spaces"]
        ).tokenize()
        test_tokens = [
            Token("identifier", "option"),
            Token("operator", "="),
            Token("identifier", "value"),
            Token("identifier", "option2"),
            Token("operator", "="),
            Token("identifier", "value2,value2"),
            Token("identifier", "option3"),
            Token("operator", "="),
            Token("identifier", "value with spaces"),
        ]
        self.assertEqual(tokens, test_tokens)
