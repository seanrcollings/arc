from typing import List, Set, Tuple, Dict, Union
from tests.base_test import BaseTest
from arc.errors import ConversionError
from arc.convert import AliasConverter as ca


class TestAliasConverter(BaseTest):
    def test_unsupported_type(self):
        with self.assertRaises(ConversionError):
            ca(Dict[str, int]).convert("")

        with self.assertRaises(ConversionError):
            ca(int).convert("")

        with self.assertRaises(ConversionError):
            ca(List[Union[int]]).convert("")

    def test_union_alias(self):
        self.assertEqual(ca(Union[int, str]).convert("1234"), 1234)
        self.assertEqual(ca(Union[int, str]).convert("1,234"), "1,234")
        self.assertEqual(ca(Union[int, bool]).convert(","), True)
        self.assertEqual(ca(Union[int, bool]).convert(""), False)
        self.assertEqual(ca(Union[str, int]).convert("1234"), "1234")
        self.assertEqual(
            ca(Union[List[int], int]).convert("1,2,3,4,5"), [1, 2, 3, 4, 5]
        )

    def test_list_alias(self):
        lst = ca(List[int]).convert("1,2,3,4,5")
        self.assertEqual(lst, [1, 2, 3, 4, 5])

        lst = ca(List[str]).convert("word,word,word")
        self.assertEqual(lst, ["word", "word", "word"])

        lst = ca(List[bool]).convert("afeaf,afeaf,")
        self.assertEqual(lst, [True, True, False])

    def test_set_alias(self):
        st = ca(Set[int]).convert("1,2,3,4,5")
        self.assertEqual(st, {1, 2, 3, 4, 5})

        st = ca(Set[int]).convert("1,2,3,4,5,1,2,3,4,5")
        self.assertEqual(st, {1, 2, 3, 4, 5})

        st = ca(Set[str]).convert("word,word,word")
        self.assertEqual(st, {"word", "word", "word"})

        st = ca(Set[bool]).convert("afeaf,afeaf,")
        self.assertEqual(st, {True, True, False})

    def test_tuple_alias(self):
        tup = ca(Tuple[int, int, int, int, int]).convert("1,2,3,4,5")
        self.assertEqual(tup, (1, 2, 3, 4, 5))

        tup = ca(Tuple[str, str, str]).convert("word,word,word")
        self.assertEqual(tup, ("word", "word", "word"))

        tup = ca(Tuple[int, str, int, str]).convert("1,word,2,word")
        self.assertEqual(tup, (1, "word", 2, "word"))

        with self.assertRaises(ConversionError):
            tup = ca(Tuple[int, str, int]).convert("1,word,2,word")
