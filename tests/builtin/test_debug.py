import pytest
from io import StringIO
from unittest.mock import patch

from arc.builtin.debug import debug
from arc import CLI


@pytest.fixture
def debug_cli(cli: CLI):
    cli.install_command(debug)
    return cli


class TestDebug:
    """For now, just test if these execute at all, not what they return"""

    def test_installed(self, debug_cli: CLI):
        assert debug is debug_cli.subcommands[debug.name]

    def test_config(self, debug_cli: CLI):
        debug_cli("debug:config")

    def test_converters(self, debug_cli: CLI):
        debug_cli("debug:aliases")

    def test_arcfile(self, debug_cli: CLI):
        debug_cli("debug:arcfile")
