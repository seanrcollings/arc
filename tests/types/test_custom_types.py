import pytest
import arc
from arc import errors


def test_convert():
    class TestType:
        def __init__(self, value: str):
            self.value = value

        @classmethod
        def __convert__(cls, value):
            return cls(value)

    @arc.command()
    def command(val: TestType):
        return val

    res = command("2")
    assert isinstance(res, TestType)
    assert res.value == "2"


def test_protocol_violation():
    class NoConvert:
        ...

    with pytest.raises(errors.ParamError):

        @arc.command()
        def c1(val: NoConvert):
            return val


def test_cleanup():
    class CleanupError(Exception):
        ...

    class TestType:
        def __init__(self, value: str):
            self.value = value

        @classmethod
        def __convert__(cls, value, info, state):
            return cls(value)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, trace):
            assert self.value == "2"
            raise CleanupError()

    @arc.command()
    def c(val: TestType):
        return val

    with pytest.raises(CleanupError):
        c("2")
