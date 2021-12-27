import pytest
import pathlib
from arc import CLI, errors
from arc.types import path


class TestImpl:
    def test_valid(self):
        assert path.ValidPath("tests/.arc") == pathlib.Path("tests/.arc")

        with pytest.raises(ValueError):
            path.ValidPath("doesntexist")

    def test_file(self):
        assert path.FilePath("tests/.arc") == pathlib.Path("tests/.arc")

        with pytest.raises(ValueError):
            path.FilePath("doesntexist")

        with pytest.raises(ValueError):
            path.FilePath("arc")

    def test_dir(self):
        assert path.DirectoryPath("arc") == pathlib.Path("arc")

        with pytest.raises(ValueError):
            path.DirectoryPath("doesntexist")

        with pytest.raises(ValueError):
            path.DirectoryPath("tests/.arc")

    def test_strict(self):
        DirectoryPath = path.strictpath(directory=True)
        assert DirectoryPath("arc") == path.DirectoryPath("arc")

        InHomeDir = path.strictpath(matches=rf"^{pathlib.Path.home()}.+")
        assert InHomeDir("arc") == pathlib.Path("arc")

        with pytest.raises(ValueError):
            InHomeDir("/tmp")


def test_usage(cli: CLI):
    @cli.command()
    def pa(path: path.ValidPath):
        return path

    assert cli("pa arc") == path.ValidPath("arc")

    with pytest.raises(errors.InvalidParamaterError):
        cli("pa doesnotexist")