import pytest

from arc import CLI


@pytest.fixture
def cli():
    # cli = mock_command("cli", CLI, arcfile="tests/.arc")
    cli = CLI(arcfile="tests/.arc")

    @cli.subcommand()
    def func1(x):
        assert isinstance(x, str)

    @cli.subcommand()
    @cli.subcommand("func2copy")
    def func2(x: int):
        assert isinstance(x, int)

    return cli
