import pytest

from arc import CLI, logging, configure

logger = logging.getArcLogger()


@pytest.fixture
def cli():
    configure(environment="development")
    cli = CLI(name="test")

    return cli
