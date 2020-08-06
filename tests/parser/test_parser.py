from tests.base_test import BaseTest
from arc.parser import Parser
from arc.parser.data_classes import Token, ScriptNode, UtilNode
from arc.errors import ParserError


class TestParser(BaseTest):
    TEST_TOKENS = [
        Token("utility", "util:"),
        Token("script", "script"),
        Token("option", "option=value"),
        Token("option", "option=value"),
        Token("flag", "--flag"),
    ]

    def test_fail(self):
        with self.assertRaises(ParserError):
            Parser("").parse()

    def test_util_parse(self):
        tree = Parser([Token("utility", "name:")]).parse()
        self.assertIsInstance(tree, UtilNode)
        self.assertEqual(tree.name, "name")

    def test_script_parse(self):
        tree = Parser([Token("script", "name")]).parse()
        self.assertIsInstance(tree, ScriptNode)
        self.assertEqual(tree.name, "name")

    def test_anon_parse(self):
        tree = Parser([Token("option", "option=value")]).parse()
        self.assertIsInstance(tree, ScriptNode)
        self.assertEqual(tree.name, "anon")

        tree = Parser(
            [Token("utility", "util:"), Token("option", "option=value")]
        ).parse()
        self.assertIsInstance(tree, UtilNode)
        self.assertEqual(tree.script.name, "anon")

    def test_parses(self):
        tree = Parser(self.TEST_TOKENS.copy()).parse()
        self.assertIsInstance(tree, UtilNode)
        self.assertIsInstance(tree.script, ScriptNode)
        self.assertEqual(len(tree.script.options), 2)
        self.assertEqual(len(tree.script.flags), 1)

    def test_consume(self):
        parser = Parser(self.TEST_TOKENS.copy())
        with self.assertRaises(ParserError):
            parser.consume("something")

        for token in self.TEST_TOKENS:
            self.assertEqual(token, parser.consume(token.type))

        # Since the above loop consumes all the tokens
        # attemptint to consume again will raise an exception
        with self.assertRaises(ParserError):
            parser.consume("something")

    def test_peek(self):
        parser = Parser(self.TEST_TOKENS.copy())
        for token in self.TEST_TOKENS:
            self.assertTrue(parser.peek(token.type))
            self.assertEqual(token, parser.consume(token.type))

        # Will always return false when parser.tokens is emtpy
        self.assertFalse(parser.peek("anything"))
