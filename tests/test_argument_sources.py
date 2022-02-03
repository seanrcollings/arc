import io
import os
import contextlib
import typing as t

import pytest

from arc import CLI, Argument, Option, errors, Context
from tests.utils import environ
from arc.prompt.helpers import ARROW_DOWN


class TestEnv:
    def test_basic(self, cli: CLI):
        @cli.command()
        def env(val: int = Argument(envvar="VAL")):
            return val

        assert cli("env 10") == 10

        with pytest.raises(errors.MissingArgError):
            cli("env")

        with environ(VAL="2"):
            assert cli("env") == 2

    def test_prefix(self, cli: CLI):
        Context._meta["env_prefix"] = "TEST_"

        try:

            @cli.command()
            def env(val: int = Argument(envvar="VAL")):
                return val

            with environ(TEST_VAL="2"):
                assert cli("env") == 2
        finally:
            Context._meta["env_prefix"] = ""

    def test_multiple(self, cli: CLI):
        @cli.command()
        def env(val: int = Argument(envvar="VAL"), key: int = Option(envvar="KEY")):
            return val, key

        assert cli("env 10 --key 10") == (10, 10)

        with pytest.raises(errors.MissingArgError):
            cli("env")

        with pytest.raises(errors.MissingArgError):
            cli("env 10")

        with environ(VAL="2", KEY="10"):
            assert cli("env") == (2, 10)

        with environ(VAL="2"):
            with pytest.raises(errors.MissingArgError):
                cli("env")

            assert cli("env --key 10") == (2, 10)


class TestPrompt:
    def test_basic(self, cli: CLI, monkeypatch: pytest.MonkeyPatch):
        @cli.command()
        def pr(val: int = Argument(prompt="Val")):
            return val

        assert cli("pr 2") == 2

        monkeypatch.setattr("sys.stdin", io.StringIO("2"))
        assert cli("pr") == 2

    def test_default(self, cli: CLI, monkeypatch: pytest.MonkeyPatch):
        @cli.command()
        def pr(val: int = Argument(prompt="Val", default=10)):
            return val

        assert cli("pr 2") == 2

        monkeypatch.setattr("sys.stdin", io.StringIO("\n"))
        assert cli("pr") == 10

    # Can't test because StringIO cannot be converted to 'raw' mode
    # def test_select_prompt(self, cli: CLI, monkeypatch: pytest.MonkeyPatch):
    #     @cli.command()
    #     def pr(val: t.Literal["a", 1] = Argument(prompt="Val")):
    #         return val

    #     assert cli("pr a") == "a"
    #     assert cli("pr 1") == 1

    #     monkeypatch.setattr("sys.stdin", io.StringIO("\n"))
    #     assert cli("pr") == "a"
    #     monkeypatch.setattr("sys.stdin", io.StringIO(f"{ARROW_DOWN}\n"))
    #     assert cli("pr") == 1


def test_precedence(cli: CLI, monkeypatch: pytest.MonkeyPatch):
    @cli.command()
    def c1(val: int = Argument(envvar="VAL", prompt="val")):
        return val

    monkeypatch.setattr("sys.stdin", io.StringIO("2"))

    with environ(VAL="3"):
        assert cli("c1") == 3

    assert cli("c1") == 2
