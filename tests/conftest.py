import logging
import pytest

from arc import CLI, ParsingMethod

logger = logging.getLogger("arc_logger")


@pytest.fixture
def cli():
    # logger.setLevel(logging.ERROR)
    cli = CLI(parsing_method=ParsingMethod.KEYWORD, arcfile="tests/.arc")

    @cli.subcommand()
    def func1(x):
        assert isinstance(x, str)
        return x

    @cli.subcommand()
    @cli.subcommand("func2copy")
    def func2(x: int):
        assert isinstance(x, int)
        return x

    return cli
