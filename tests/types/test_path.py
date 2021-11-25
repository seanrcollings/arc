import pytest
import pathlib
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
