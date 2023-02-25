import pytest
import pathlib
import arc
from arc import errors
from arc.types import path


class TestImpl:
    def test_valid(self):
        assert arc.convert("tests/conftest.py", path.ValidPath) == pathlib.Path(
            "tests/conftest.py"
        )

        with pytest.raises(errors.ValidationError):
            arc.convert("doesnotexist", path.ValidPath)

    def test_file(self):
        assert arc.convert("tests/conftest.py", path.FilePath) == pathlib.Path(
            "tests/conftest.py"
        )

        with pytest.raises(errors.ValidationError):
            arc.convert("doesnotexist", path.FilePath)

        with pytest.raises(errors.ValidationError):
            arc.convert("arc", path.FilePath)

    def test_dir(self):
        assert arc.convert("arc", path.DirectoryPath) == pathlib.Path("arc")

        with pytest.raises(errors.ValidationError):
            arc.convert("doesntexist", path.DirectoryPath)

        with pytest.raises(errors.ValidationError):
            arc.convert("tests/conftest.py", path.DirectoryPath)


def test_usage():
    @arc.command
    def pa(path: path.ValidPath):
        return path

    assert pa("arc") == path.ValidPath("arc")

    with pytest.raises(errors.InvalidArgValue):
        pa("doesnotexist")
