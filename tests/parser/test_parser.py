from unittest import TestCase
from arc.parser import Parser, Tokenizer
from arc.parser.data_types import CommandNode


class TestParser(TestCase):
    TEST_UTIL_TOKENS = Tokenizer(
        ["util:command", "option=value", "option=value", "--flag"]
    ).tokenize()

    TEST_SCRIPT_TOKENS = Tokenizer(
        ["command", "option=value", "option=value", "--flag"]
    ).tokenize()

    def test_util_parse(self):
        command = Parser(self.TEST_UTIL_TOKENS).parse()
        self.assertIsInstance(command, CommandNode)
        self.assertEqual(command.namespace, ["util", "command"])

    def test_script_parse(self):
        command = Parser(self.TEST_SCRIPT_TOKENS).parse()
        self.assertIsInstance(command, CommandNode)
        self.assertEqual(command.namespace, ["command"])

    # def test_anon_parse(self):
    #     command = Parser([Token("option", "option=value")]).parse()
    #     self.assertIsInstance(command, ScriptNode)
    #     self.assertEqual(command.name, "anon")

    #     command = Parser(
    #         [Token("utility", "util:"), Token("option", "option=value")]
    #     ).parse()
    #     self.assertIsInstance(command, UtilNode)
    #     self.assertEqual(command.command.name, "anon")

    def test_parses(self):
        command = Parser(self.TEST_UTIL_TOKENS.copy()).parse()
        self.assertEqual(len(command.args), 3)

    def test_consume(self):
        parser = Parser(self.TEST_UTIL_TOKENS.copy())
        with self.assertRaises(ValueError):
            parser.consume("something")

        for token in self.TEST_UTIL_TOKENS:
            self.assertEqual(token.value, parser.consume(token.type))

        # Since the above loop consumes all the tokens
        # attempting to consume again will raise an exception
        with self.assertRaises(IndexError):
            parser.consume("something")

    def test_peek(self):
        parser = Parser(self.TEST_UTIL_TOKENS.copy())
        for token in self.TEST_UTIL_TOKENS:
            self.assertEqual(parser.peek(), token.type)
            self.assertEqual(token.value, parser.consume(token.type))

        # Will always return false when parser.tokens is emtpy
        self.assertFalse(parser.peek() == "anything")
