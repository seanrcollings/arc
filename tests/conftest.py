import pytest

from arc import CLI
from .mock import mock_command, mock_typed_func, MockedCommand


@pytest.fixture
def cli():
    cli = mock_command("cli", CLI)

    def base(val: int):
        ...

    mocked = mock_typed_func(base)
    cli.base()(mocked)

    @cli.subcommand()
    def func1(x):
        ...

    @cli.subcommand()
    @cli.subcommand("func2copy")
    def func2(x: int):
        ...

    return cli
