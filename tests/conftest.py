import pytest

from arc import CLI, logging

logger = logging.getArcLogger()


@pytest.fixture
def cli():
    cli = CLI(config_file="tests/.arc")
    logger.setLevel(logging.CRITICAL)

    return cli
