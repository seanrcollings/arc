import unittest

from arc import namespace

# MockCommand's implementation is not easy to use in this scenario,
# so these tests just dig into the objects themselves for now
class TestNamespace(unittest.TestCase):
    def setUp(self) -> None:
        self.namespace = namespace("namespace", context={"test": 0})

    def test_context(self):
        self.assertEqual(self.namespace.context, {"test": 0})
        parent = namespace("parent", context={"test2": 1})
        parent.install_command(self.namespace)
        self.assertEqual(self.namespace.context, {"test": 0, "test2": 1})

    def test_base(self):
        @self.namespace.base(context={"test2": 0})
        def base_command(val: int):
            ...

        self.assertEqual(self.namespace, base_command)
        self.assertEqual(self.namespace.context, {"test": 0, "test2": 0})
        self.assertEqual(self.namespace.args["val"].annotation, int)
