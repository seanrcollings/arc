import typing as t
from pathlib import Path
import pytest
from arc import CLI
from arc.types import File


@pytest.mark.parametrize(
    "mode",
    [
        File.Read,
        File.Write,
        File.ReadWrite,
        File.Append,
        File.AppendRead,
        File.BinaryRead,
        File.BinaryWrite,
        File.BinaryReadWrite,
        File.BinaryAppend,
        File.BinaryAppendRead,
    ],
)
def test_mode(cli: CLI, mode, tmp_path: Path):
    mode_str = t.get_args(mode)[-1]
    name = tmp_path / "test_mode"
    name.touch()

    @cli.command()
    def command(file: mode):  # type: ignore
        return file

    file = cli(f"command {name}")
    assert file.closed
    assert file.mode == mode_str


def test_read(cli: CLI):
    @cli.command()
    def read(file: File.Read):
        return file, file.read()

    file, contents = cli("read tests/.arc")
    assert file.closed
    assert file.mode == "r"
    assert contents == "mode=development"


def test_binary_read(cli: CLI):
    @cli.command()
    def read(file: File.BinaryRead):
        return file, file.read()

    file, contents = cli("read tests/.arc")
    assert file.closed
    assert file.mode == "rb"
    assert contents == b"mode=development"


def test_write(cli: CLI, tmp_path: Path):
    @cli.command()
    def write(file: File.Write):
        file.write("test")
        return file

    name = tmp_path / "test_write"

    assert cli(f"write {name}").closed

    with open(name) as f:
        assert f.read() == "test"
