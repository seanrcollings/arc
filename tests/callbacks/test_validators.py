from typing import TextIO
import pytest
from pathlib import Path
from arc import CLI, callbacks, errors


def test_in_range(cli: CLI):
    @callbacks.in_range("val", 1, 10)
    @cli.command()
    def test(val: int):
        return val

    assert cli("test 2") == 2
    assert cli("test 1") == 1
    assert cli("test 10") == 10

    with pytest.raises(errors.ValidationError):
        cli("test 99")


def test_valid_path_str(cli: CLI):
    @callbacks.valid_path("path")
    @cli.subcommand()
    def test(path: str):
        return path

    assert cli("test arc") == "arc"

    with pytest.raises(errors.ValidationError):
        cli("test ainfea")


def test_valid_path(cli: CLI):
    @callbacks.valid_path("path")
    @cli.subcommand()
    def test(path: Path):
        return path

    assert cli("test arc") == Path("arc")

    with pytest.raises(errors.ValidationError):
        cli("test ainfea")
