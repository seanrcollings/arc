from typing import TextIO
import pytest
from arc import CLI, callbacks, errors


def test_open_file(cli: CLI):
    @callbacks.open_file("file", "r")
    @cli.subcommand()
    def test(file: TextIO):
        assert not file.closed
        return file

    assert cli("test file=.arc").closed

    with pytest.raises(errors.ActionError):
        cli("test file=doesnotexist")
