from ast import Call
import pytest
from arc import Context, errors, decorator
import arc


class CallbackException(Exception):
    """Used to assert that decorators are actually running"""

    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_execute():
    @decorator()
    def cb():
        raise CallbackException()

    @cb
    @arc.command()
    def test():
        return 10

    with pytest.raises(CallbackException):
        test("")

    cb.remove(test)
    assert test("") == 10


def test_exception():
    @decorator()
    def cb():
        try:
            yield
        except errors.ExecutionError:
            raise CallbackException()

    @cb
    @arc.command()
    def test():
        raise errors.ExecutionError()

    with pytest.raises(CallbackException):
        test("")


def test_final():
    @decorator()
    def cb():
        try:
            yield
        finally:
            raise CallbackException()

    @cb
    @arc.command()
    def test1():
        raise errors.ExecutionError()

    @cb
    @arc.command()
    def test2():
        ...

    with pytest.raises(CallbackException):
        test1("")

    with pytest.raises(CallbackException):
        test2("")


def test_missing_yield():
    """A pure function should still execute"""

    @decorator()
    def cb():
        raise CallbackException()

    @cb
    @arc.command()
    def command():
        ...

    with pytest.raises(CallbackException):
        command("")


def test_deco_inheritance():
    @arc.decorator()
    def cb1(
        args,
    ):
        ...

    @cb1
    @arc.command()
    def command():
        ...

    @command.subcommand()
    def sub():
        ...

    assert cb1 in sub.decorators()


def test_decorator_order():
    callback_order = []

    @arc.decorator()
    def cb1():
        callback_order.append("cb1")
        yield
        callback_order.append("cb1")

    @arc.decorator()
    def cb2():
        callback_order.append("cb2")
        yield
        callback_order.append("cb2")

    @cb1
    @cb2
    @arc.command()
    def command():
        ...

    command()
    assert callback_order == ["cb1", "cb2", "cb2", "cb1"]


def test_children_only():
    @arc.decorator(children_only=True)
    def cb():
        raise CallbackException()

    @arc.command()
    def command():
        ...

    @cb
    @command.subcommand()
    def sub1():
        ...

    @sub1.subcommand()
    def sub2():
        ...

    command("sub1")

    with pytest.raises(CallbackException):
        command("sub1 sub2")


# We don't annotate the root object in these cases
# because they will always execute their decorators when
# the global parameters get validated.


def test_remove_decorator():
    @arc.decorator(children_only=True)
    def cb():
        raise CallbackException()

    @arc.command()
    def root():
        ...

    @cb
    @root.subcommand()
    def c1():
        ...

    @c1.subcommand()
    def sub1():
        ...

    @cb.remove
    @c1.subcommand()
    def c2():
        ...

    @c2.subcommand()
    def sub2():
        ...

    with pytest.raises(CallbackException):
        root("c1 sub1")

    # Shouldn't raise, because the decorator isn't present
    root("c1 c2")
    root("c1 c2 sub2")


def test_non_inheritable():
    @arc.decorator(inherit=False)
    def cb():
        raise CallbackException()

    @arc.command()
    def command():
        ...

    @cb
    @command.subcommand()
    def sub1():
        ...

    @sub1.subcommand()
    def sub2():
        ...

    with pytest.raises(CallbackException):
        command("sub1")

    command("sub1 sub2")


def test_install_order():
    @arc.decorator()
    def deco():
        raise CallbackException()

    @arc.command()
    def command():
        ...

    @deco
    @command.subcommand()
    def sub():
        ...

    @arc.command()
    def sub2():
        ...

    @sub2.subcommand()
    def sub3():
        ...

    sub.add_command(sub2)

    with pytest.raises(CallbackException):
        command("sub sub2 sub3")
