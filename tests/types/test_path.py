import pytest
import pathlib
from arc import CLI
from arc.types import path


class TestImpl:
    def test_valid(self):
        assert path.ValidPath(".arc") == pathlib.Path(".arc")

        with pytest.raises(ValueError):
            path.ValidPath("doesntexist")

    def test_file(self):
        assert path.FilePath(".arc") == pathlib.Path(".arc")

        with pytest.raises(ValueError):
            path.FilePath("doesntexist")

        with pytest.raises(ValueError):
            path.FilePath("arc")

    def test_dir(self):
        assert path.DirectoryPath("arc") == pathlib.Path("arc")

        with pytest.raises(ValueError):
            path.DirectoryPath("doesntexist")

        with pytest.raises(ValueError):
            path.DirectoryPath(".arc")

    def test_strict(self):
        DirectoryPath = path.strictpath(directory=True)
        assert DirectoryPath("arc") == path.DirectoryPath("arc")

        MatchPath = path.strictpath(matches="^/home/sean/.+")
        assert MatchPath("arc") == pathlib.Path("arc")

        with pytest.raises(ValueError):
            MatchPath("/tmp")


def test_usage(cli: CLI):
    @cli.command()
    def pa(path: path.ValidPath):
        return path

    assert cli("pa arc") == path.ValidPath("arc")

    with pytest.raises(ValueError):
        cli("pa doesnotexist")