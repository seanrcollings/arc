import io

import pytest

import arc
from arc import Argument, Option, errors, configure
from arc import constants
from arc.define.param.param import Param, ValueOrigin
from tests.utils import environ  # type: ignore
from arc.prompt.helpers import ARROW_DOWN


class TestEnv:
    def test_basic(self):
        @arc.command
        def env(val: int = Argument(envvar="VAL")):
            return val

        assert env("10") == 10

        with pytest.raises(errors.MissingArgError):
            env("")

        with environ(VAL="2"):
            assert env("") == 2

    def test_prefix(self):
        configure(env_prefix="TEST_")

        try:

            @arc.command
            def env(val: int = Argument(envvar="VAL")):
                return val

            with environ(TEST_VAL="2"):
                assert env("") == 2
        finally:
            configure(env_prefix="")

    def test_multiple(self):
        @arc.command
        def env(val: int = Argument(envvar="VAL"), key: int = Option(envvar="KEY")):
            return val, key

        assert env("10 --key 10") == (10, 10)

        with pytest.raises(errors.MissingArgError):
            env("")

        with pytest.raises(errors.MissingArgError):
            env("10")

        with environ(VAL="2", KEY="10"):
            assert env("") == (2, 10)

        with environ(VAL="2"):
            with pytest.raises(errors.MissingArgError):
                env("")

            assert env("--key 10") == (2, 10)

    def test_get_origin(self):
        @arc.command
        def env(ctx: arc.Context, val: int = Argument(envvar="VAL")):
            return ctx.get_origin("val")

        assert env("2") == ValueOrigin.CLI

        with environ(VAL="2"):
            assert env("") == ValueOrigin.ENV


class TestPrompt:
    def test_basic(self, monkeypatch: pytest.MonkeyPatch):
        @arc.command
        def pr(val: int = Argument(prompt="Val")):
            return val

        assert pr("2") == 2

        monkeypatch.setattr("sys.stdin", io.StringIO("2"))
        assert pr("") == 2

    def test_default(self, monkeypatch: pytest.MonkeyPatch):
        @arc.command
        def pr(val: int = Argument(prompt="Val", default=10)):
            return val

        assert pr("2") == 2

        monkeypatch.setattr("sys.stdin", io.StringIO("\n"))
        assert pr("") == 10

    def test_get_origin(self, monkeypatch: pytest.MonkeyPatch):
        @arc.command
        def pr(ctx: arc.Context, val: int = Argument(prompt="Val")):
            return ctx.get_origin("val")

        monkeypatch.setattr("sys.stdin", io.StringIO("2"))
        assert pr("") == ValueOrigin.PROMPT


class TestGetter:
    def test_basic(self):
        def _get(param: Param):
            return 2

        @arc.command
        def getter(val: int = Argument(get=_get, default=1)):
            return val

        assert getter("") == 2

    def test_alias(self):
        @arc.command
        def getter(val: int = Argument(default=1)):
            return val

        @getter.get("val")
        def get_val(param):
            return 2

        assert getter("") == 2

    def test_missing(self):
        @arc.command
        def getter(val: int = Argument()):
            return val

        @getter.get("val")
        def get_val(param):
            return constants.MISSING

        with pytest.raises(errors.MissingArgError):
            getter("")

    def test_missing_with_default(self):
        @arc.command
        def getter(val: int = Argument(default=1)):
            return val

        @getter.get("val")
        def get_val(param):
            return constants.MISSING

        assert getter("") == 1

    def test_get_origin(self):
        @arc.command
        def getter(ctx: arc.Context, val: int = Argument(default=1)):
            return ctx.get_origin("val")

        @getter.get("val")
        def get_val(param):
            return 2

        assert getter("") == ValueOrigin.GETTER


def test_precedence(monkeypatch: pytest.MonkeyPatch):
    @arc.command
    def c1(val: int = Argument(envvar="VAL", prompt="val")):
        return val

    monkeypatch.setattr("sys.stdin", io.StringIO("2"))

    with environ(VAL="3"):
        assert c1("") == 3

    assert c1("") == 2
