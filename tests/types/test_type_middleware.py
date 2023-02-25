import typing as t
import arc
from arc.types.transforms import Round


def test_middleware_exec():
    @arc.command
    def com(val: t.Annotated[float, Round(2)]):
        return val

    assert com("1.123456") == 1.12


def test_middleware_injected():
    def _get():
        return 1.123456

    @arc.command
    def com(val: t.Annotated[float, Round(2)] = arc.Depends(_get)):
        return val

    assert com("") == 1.12
