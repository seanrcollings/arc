import pytest
import pathlib
import arc
from arc import errors
from arc.types import path


class TestImpl:
    def test_valid(self):
        assert path.ValidPath("tests/conftest.py") == pathlib.Path("tests/conftest.py")

        with pytest.raises(ValueError):
            path.ValidPath("doesntexist")

    def test_file(self):
        assert path.FilePath("tests/conftest.py") == pathlib.Path("tests/conftest.py")

        with pytest.raises(ValueError):
            path.FilePath("doesntexist")

        with pytest.raises(ValueError):
            path.FilePath("arc")

    def test_dir(self):
        assert path.DirectoryPath("arc") == pathlib.Path("arc")

        with pytest.raises(ValueError):
            path.DirectoryPath("doesntexist")

        with pytest.raises(ValueError):
            path.DirectoryPath("tests/conftest.py")

    def test_strict(self):
        class InHomeDir(path.ValidPath):
            valid = False
            matches = rf"^{pathlib.Path.home()}.*"

        assert (
            InHomeDir(str(pathlib.Path.home() / "something"))
            == pathlib.Path.home() / "something"
        )

        with pytest.raises(ValueError):
            InHomeDir("/tmp")


def test_usage():
    @arc.command()
    def pa(path: path.ValidPath):
        return path

    assert pa("arc") == path.ValidPath("arc")

    with pytest.raises(errors.InvalidArgValue):
        pa("doesnotexist")
