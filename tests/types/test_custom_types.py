import pytest
from arc import CLI, errors


def test_convert(cli: CLI):
    class TestType:
        def __init__(self, value: str):
            self.value = value

        @classmethod
        def __convert__(cls, value, param_type):
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


def test_config_updating(cli: CLI):
    class TestType:
        class Config:
            name = "TestType"
            allow_missing = True
            allowed_annotated_args = 2

        def __init__(self, value: str):
            self.value = value

        @classmethod
        def __convert__(cls, value, param_type):
            # Give us easy access to the param_type
            return param_type

    @cli.command()
    def c(val: TestType):
        return val

    param_type = cli("c")
    assert param_type.Config.name == TestType.Config.name
    assert param_type.Config.allow_missing == TestType.Config.allow_missing
    assert (
        param_type.Config.allowed_annotated_args
        == TestType.Config.allowed_annotated_args
    )


def test_cleanup(cli: CLI):
    class TestType:
        class Config:
            name = "TestType"
            allow_missing = True
            allowed_annotated_args = 2

        def __init__(self, value: str):
            self.value = value

        @classmethod
        def __convert__(cls, value, param_type):
            # Give us easy access to the param_type
            return cls(value)

        def __cleanup__(self):
            ...

    @cli.command()
    def c(val: TestType):
        return val

    assert cli("c 2").__cleanup__ in c.executable.params["val"]._cleanup_funcs
