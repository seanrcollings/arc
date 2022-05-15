from unittest import mock
import pytest
from arc import CLI


def test_execution(cli: CLI):
    @cli.command()
    def command():
        raise Exception("failure")

    func = mock.MagicMock(name="handler")
    command.handle(Exception)(func)

    cli("command")
    assert func.call_count == 1


def test_multi_execution(cli: CLI):
    @cli.command()
    def command():
        raise Exception("failure")

    def handler_1(exc, _ctx):
        raise exc

    func1 = mock.MagicMock(name="handler_1", side_effect=handler_1)
    command.handle(Exception)(func1)

    with pytest.raises(Exception):
        cli("command")

    func2 = mock.MagicMock(name="handler_2")
    command.handle(Exception)(func2)

    cli("command")
    assert func1.call_count == 2
    assert func2.call_count == 1
