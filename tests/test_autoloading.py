from pathlib import Path
import pytest

import arc


@pytest.fixture(scope="function")
def autoload_path(tmp_path_factory: pytest.TempPathFactory):
    path = tmp_path_factory.mktemp("data") / "test_autoload.py"
    with path.open("w") as f:
        f.write(
            """
import arc

@arc.command()
def test():
    return 2

"""
        )
    return path


def test_autoload(autoload_path: Path):
    @arc.command()
    def command():
        ...

    command.autoload(str(autoload_path))
    assert "test" in command.subcommands


def test_overwrite_allowed(autoload_path: Path):
    arc.configure(autoload_overwrite=True)

    @arc.command()
    def command():
        ...

    @command.subcommand()
    def test():
        return 1

    command.autoload(str(autoload_path))
    assert command("test") == 2


def test_overwrite_disallowed(autoload_path: Path):
    arc.configure(autoload_overwrite=False)

    @arc.command()
    def command():
        ...

    @command.subcommand()
    def test():
        ...

    with pytest.raises(arc.errors.CommandError):
        command.autoload(str(autoload_path))

    arc.configure(autoload_overwrite=True)
