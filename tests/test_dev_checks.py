import pytest
import contextlib
import arc
from arc import errors
from arc.config import Config
import arc.typing as at

config = Config.load()


@contextlib.contextmanager
def set_env(env: at.Env):
    prev = config.environment
    try:
        arc.configure(environment=env)
        yield
    finally:
        arc.configure(environment=prev)


def test_no_pos_only():
    @arc.command
    def command(val1, /, val2):
        ...

    with pytest.raises(errors.ParamError):
        command()


def test_depends_default():
    @arc.command
    def command(ctx: arc.State = 2):  # type: ignore
        ...

    with pytest.raises(errors.ParamError):
        command()


def test_group_default():
    @arc.group
    class Group:
        ...

    @arc.command
    def command(ctx: Group = object()):  # type: ignore
        ...

    with pytest.raises(errors.ParamError):
        command()
