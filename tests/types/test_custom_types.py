import pytest
from arc import CLI, errors


def test_convert(cli: CLI):
    class TestType:
        def __init__(self, value: str):
            self.value = value

        @classmethod
        def __convert__(cls, value):
            return cls(value)

    @cli.command()
    def command(val: TestType):
        return val

    res = cli("command 2")
    assert isinstance(res, TestType)
    assert res.value == "2"


def test_protocol_violation(cli: CLI):
    class NoConvert:
        ...

    class NonClassMethod:
        def __convert__(self, value, param_type):
            ...

    @cli.command()
    def c1(val: NoConvert):
        return val

    @cli.command()
    def c2(val: NonClassMethod):
        return val

    with pytest.raises(errors.MissingParamType):
        cli("c1")

    with pytest.raises(errors.ArgumentError):
        cli("c2")


def test_cleanup(cli: CLI):
    class CleanupError(Exception):
        ...

    class TestType:
        def __init__(self, value: str):
            self.value = value

        @classmethod
        def __convert__(cls, value, info, state):
            return cls(value)

        def __exit__(self, exc_type, exc_value, trace):
            assert self.value == "2"
            raise CleanupError()

    @cli.command()
    def c(val: TestType):
        return val

    with pytest.raises(CleanupError):
        cli("c 2")
