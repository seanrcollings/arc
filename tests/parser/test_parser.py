from tests.base_test import BaseTest
from arc.parser import Parser, Tokenizer
from arc.parser.data_types import ScriptNode, UtilNode
from arc.errors import ParserError


class TestParser(BaseTest):
    TEST_TOKENS = Tokenizer(
        ["util:script", "option=value", "option=value", "--flag"]
    ).tokenize()

    def test_util_parse(self):
        tree = Parser(self.TEST_TOKENS[0:3]).parse()
        self.assertIsInstance(tree, UtilNode)
        self.assertEqual(tree.name, "util")

    def test_script_parse(self):
        tree = Parser([self.TEST_TOKENS[2]]).parse()
        self.assertIsInstance(tree, ScriptNode)
        self.assertEqual(tree.name, "script")

    # def test_anon_parse(self):
    #     tree = Parser([Token("option", "option=value")]).parse()
    #     self.assertIsInstance(tree, ScriptNode)
    #     self.assertEqual(tree.name, "anon")

    #     tree = Parser(
    #         [Token("utility", "util:"), Token("option", "option=value")]
    #     ).parse()
    #     self.assertIsInstance(tree, UtilNode)
    #     self.assertEqual(tree.script.name, "anon")

    def test_parses(self):
        tree = Parser(self.TEST_TOKENS.copy()).parse()
        self.assertIsInstance(tree, UtilNode)
        self.assertIsInstance(tree.script, ScriptNode)
        self.assertEqual(len(tree.script.args), 3)

    def test_consume(self):
        parser = Parser(self.TEST_TOKENS.copy())
        with self.assertRaises(ValueError):
            parser.consume("something")

        for token in self.TEST_TOKENS:
            self.assertEqual(token.value, parser.consume(token.type))

        # Since the above loop consumes all the tokens
        # attempting to consume again will raise an exception
        with self.assertRaises(IndexError):
            parser.consume("something")

    def test_peek(self):
        parser = Parser(self.TEST_TOKENS.copy())
        for token in self.TEST_TOKENS:
            self.assertEqual(parser.peek(), token.type)
            self.assertEqual(token.value, parser.consume(token.type))

        # Will always return false when parser.tokens is emtpy
        self.assertFalse(parser.peek() == "anything")
