from unittest.mock import create_autospec
import pytest

from arc import callbacks, errors, CLI


@callbacks.before
def raise_before(_):
    raise errors.ValidationError()


@callbacks.after
def raise_after(_):
    raise errors.ValidationError()


def test_exec_time(cli: CLI):
    @raise_before
    @cli.subcommand()
    def top():
        assert False

    with pytest.raises(errors.ValidationError):
        cli("top")

    # assert top.function.call_count == 0

    @raise_after
    @cli.subcommand()
    def bottom():
        assert True

    with pytest.raises(errors.ValidationError):
        cli("bottom")

    # assert bottom.function.call_count == 1
