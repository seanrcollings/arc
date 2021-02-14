from unittest import TestCase
from arc.convert import *
from arc.errors import ConversionError


class TestConverters(TestCase):
    def test_int(self):
        self.assertEqual(IntConverter(int).convert("1"), 1)
        self.assertEqual(IntConverter(int).convert("2"), 2)
        self.assertEqual(IntConverter(int).convert("213131"), 213131)

        with self.assertRaises(ConversionError):
            IntConverter(int).convert("no numbers")

    def test_float(self):
        self.assertEqual(FloatConverter(float).convert("1"), 1.0)
        self.assertEqual(FloatConverter(float).convert("1.2"), 1.2)
        self.assertEqual(FloatConverter(float).convert("2.32"), 2.32)
        self.assertEqual(FloatConverter(float).convert("213.131"), 213.131)

        with self.assertRaises(ConversionError):
            FloatConverter(float).convert("no numbers")

    def test_byte(self):
        self.assertEqual(BytesConverter(bytes).convert("string"), b"string")

    def test_list(self):
        self.assertEqual(ListConverter(list).convert("1,2,3"), ["1", "2", "3"])
        self.assertEqual(ListConverter(list).convert("a,b,c"), ["a", "b", "c"])

        with self.assertRaises(ConversionError):
            ListConverter(list).convert("no commas")

    def test_bool(self):
        self.assertEqual(BoolConverter(bool).convert("0"), False)
        self.assertEqual(BoolConverter(bool).convert("1"), True)

        self.assertEqual(BoolConverter(bool).convert("True"), True)
        self.assertEqual(BoolConverter(bool).convert("T"), True)
        self.assertEqual(BoolConverter(bool).convert("true"), True)
        self.assertEqual(BoolConverter(bool).convert("t"), True)

        self.assertEqual(BoolConverter(bool).convert("False"), False)
        self.assertEqual(BoolConverter(bool).convert("F"), False)
        self.assertEqual(BoolConverter(bool).convert("false"), False)
        self.assertEqual(BoolConverter(bool).convert("f"), False)

        with self.assertRaises(ConversionError):
            BoolConverter(bool).convert("ainfeainfeain")
