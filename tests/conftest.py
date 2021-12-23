import pytest

from arc import CLI, logging

logger = logging.getArcLogger()


@pytest.fixture
def cli():
    cli = CLI(name="test", env="development")
    logger.setLevel(logging.CRITICAL)

    return cli
