from unittest import TestCase
from arc import run
from arc.command import Context

from .mock import mock_command


class TestContext(TestCase):
    def setUp(self):
        self.mock = mock_command("cli", context={"test": 1})

    def test_parent_context(self):
        @self.mock.subcommand()
        def parent_context(val: int, context: Context):
            ...

        @self.mock.subcommand()
        def ignore_parent_context(val: int):
            ...

        run(self.mock, "parent_context val=2")
        parent_context.function.assert_called_with(val=2, context=Context({"test": 1}))

        run(self.mock, "ignore_parent_context val=2")
        ignore_parent_context.function.assert_called_with(val=2)

    def test_my_context(self):
        @self.mock.subcommand(context={"test2": 3})
        def local_context(context: Context):
            ...

        run(self.mock, "local_context")
        local_context.function.assert_called_with(
            context=Context({"test": 1, "test2": 3})
        )

    def test_context_name(self):
        @self.mock.subcommand()
        def other_context_name(foo: Context):
            ...

        run(self.mock, "other_context_name")
        other_context_name.function.assert_called_with(foo=Context({"test": 1}))

    def test_propagate(self):
        test_namespace = mock_command("test_namespace")

        @test_namespace.subcommand(context={"test2": 2})
        def test(ctx: Context):
            ...

        self.mock.install_command(test_namespace)
        run(self.mock, "test_namespace:test")
        test.function.assert_called_with(ctx=Context({"test": 1, "test2": 2}))

    def test_custom_context(self):
        class CustomContext(Context):
            ...

        @self.mock.subcommand()
        def custom(ctx: CustomContext):
            ...

        run(self.mock, "custom")
        custom.function.assert_called_with(ctx=CustomContext({"test": 1}))
