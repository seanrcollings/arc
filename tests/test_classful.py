import pytest
from arc import CLI, errors, ParsingMethod


def test_basic(cli: CLI):
    @cli.subcommand()
    class Test:
        val: int

        def handle(self):
            return self.val

    assert cli("Test val=2") == 2

    with pytest.raises(errors.ValidationError):
        cli("Test")


def test_default(cli: CLI):
    @cli.subcommand()
    class Test:
        val: int = 2

        def handle(self):
            return self.val

    assert cli("Test") == 2
    assert cli("Test val=3") == 3


def test_short_args(cli: CLI):
    @cli.subcommand(short_args={"val": "v"})
    class Test:
        val: int

        def handle(self):
            return self.val

    assert cli("Test val=2") == 2
    assert cli("Test v=2") == 2


def test_positional(cli: CLI):
    @cli.subcommand(parsing_method=ParsingMethod.POSITIONAL)
    class Test:
        val: int

        def handle(self):
            return self.val

    assert cli("Test 2") == 2


# def test_raw(cli: CLI):
#     @cli.subcommand(parsing_method=ParsingMethod.RAW)
#     class Test:
#         val: int

#         def handle(self):
#             return self.val

#     assert cli("Test 2") == 2


def test_standard(cli: CLI):
    @cli.subcommand(parsing_method=ParsingMethod.STANDARD)
    class Test:
        val: int

        def handle(self):
            return self.val

    assert cli("Test --val 2") == 2
