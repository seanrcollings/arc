import logging
import pytest

from arc import CLI

logger = logging.getLogger("arc_logger")


@pytest.fixture
def cli():
    cli = CLI(config_file="tests/.arc")
    logger.setLevel(logging.CRITICAL)

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
