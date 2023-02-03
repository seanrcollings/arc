import pytest
import contextlib
import arc
from arc import errors
from arc.config import config
import arc.typing as at


@contextlib.contextmanager
def set_env(env: at.Env):
    prev = config.environment
    try:
        arc.configure(environment=env)
        yield
    finally:
        arc.configure(environment=prev)


def test_param_instantation():
    with set_env("production"):

        @arc.command()
        def command(val: int = 2):
            ...

        assert command.__dict__.get("param_def", None) is None

    with set_env("development"):

        @arc.command()
        def command(val: int = 2):
            ...

        assert command.__dict__.get("param_def", None) is not None


def test_no_pos_only():
    with pytest.raises(errors.ParamError):

        @arc.command()
        def command(val1, /, val2):
            ...


def test_depends_default():
    with pytest.raises(errors.ParamError):

        @arc.command()
        def command(ctx: arc.State = 2):  # type: ignore
            ...


def test_group_default():
    @arc.group
    class Group:
        ...

    with pytest.raises(errors.ParamError):

        @arc.command()
        def command(ctx: Group = Group()):  # type: ignore
            ...
