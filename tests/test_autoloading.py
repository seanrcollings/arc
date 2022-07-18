from pathlib import Path
import pytest

import arc


@pytest.fixture(scope="function")
def autoload_path(tmp_path_factory: pytest.TempPathFactory):
    path = tmp_path_factory.mktemp("data") / "test_autload.py"
    with path.open("w") as f:
        f.write(
            """
import arc

arc.configure(environment="development")


@arc.command()
def test():
    arc.print("hello there!")

"""
        )
    return path


def test_autoload(autoload_path: Path):
    @arc.command()
    def command():
        ...

    command.autoload(str(autoload_path))
    assert "test" in command.subcommands


def test_overwrite(autoload_path: Path):
    @arc.command()
    def command():
        ...

    @command.subcommand()
    def test():
        ...

    with pytest.raises(arc.errors.CommandError):
        command.autoload(str(autoload_path))
