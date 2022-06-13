import os
import typing as t
from pathlib import Path
import pytest
import arc
from arc.types import File


@pytest.fixture(scope="function")
def content_file(tmp_path_factory: pytest.TempPathFactory):
    path = tmp_path_factory.mktemp("data") / "content"
    with path.open("w") as f:
        f.write("content")
    return path


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
def test_mode(mode, content_file: Path):
    mode_str = t.get_args(mode)[-1]

    @arc.command()
    def command(file: mode):  # type: ignore
        return file

    file = command(str(content_file))
    assert file.closed
    assert file.mode == mode_str


def test_read(content_file: Path):
    @arc.command()
    def command(file: File.Read):
        return file, file.read()

    file, contents = command(str(content_file))
    assert file.closed
    assert file.mode == "r"
    assert contents == "content"


def test_binary_read(content_file: Path):
    @arc.command()
    def command(file: File.BinaryRead):
        return file, file.read()

    file, contents = command(str(content_file))
    assert file.closed
    assert file.mode == "rb"
    assert contents == b"content"


def test_write(content_file: Path):
    @arc.command()
    def command(file: File.Write):
        file.write("test")
        return file

    assert command(str(content_file)).closed

    with content_file.open() as f:
        assert f.read() == "test"
