import pytest

from arc import CLI
from arc.run import *
from arc.result import Result, Ok, Err
from arc import errors, config


@pytest.fixture
def runcli(cli: CLI):
    @cli.subcommand()
    def err():
        return Err()

    @cli.subcommand()
    def ok():
        return Ok()

    @cli.subcommand()
    def func1(x):
        assert isinstance(x, str)
        return x

    @cli.subcommand()
    @cli.subcommand("func2copy")
    def func2(x: int):
        assert isinstance(x, int)
        return x

    return cli


class TestRunFunction:
    def test_success(self, runcli: CLI):
        run(runcli, "ok") == Ok()
        run(runcli, "err") == Err()
        run(runcli, "func1 hi") == Ok("hi")
        run(runcli, "func2 2") == Ok(2)

    def test_failure(self, runcli: CLI):
        with pytest.raises(errors.ArgumentError):
            run(runcli, "func1")

        with pytest.raises(errors.ArgumentError):
            run(runcli, "func2 string")

    def test_handle_exception(self, runcli: CLI):
        config.mode = "production"
        with pytest.raises(SystemExit):
            run(runcli, "func1", handle_exception=True)

        with pytest.raises(SystemExit):
            run(runcli, "func2 string", handle_exception=True)

    def test_check_result(self, runcli: CLI):
        run(runcli, "func1 hi", check_result=True) == "hi"
        run(runcli, "func2 2", check_result=True) == 2

        config.mode = "production"
        with pytest.raises(errors.ExecutionError):
            run(runcli, "err", check_result=True)

        with pytest.raises(SystemExit):
            run(runcli, "err", check_result=True, handle_exception=True)


class TestGetCommandNamespace:
    command = "command"
    command_args = ["--name sean", "--flag", "--", "value"]
    args = [command, *command_args]

    def test_empty(self):
        assert get_command_namespace({"pos_values": []}) == []

    def test_no_namespace(self):
        assert get_command_namespace(parse(self.command_args)) == []

    def test_single(self):
        assert get_command_namespace(parse(self.args)) == [self.command]

    def test_nested(self):
        nested = "nested:command:name"
        assert get_command_namespace(
            parse([nested, *self.command_args])
        ) == nested.split(":")


class TestFindCommand:
    def test_find(self, runcli: CLI):
        @runcli.subcommand(("name1", "name2"))
        def _():
            ...

        assert find_command_chain(runcli, ["func1"])[-1] == runcli.subcommands["func1"]
        assert find_command_chain(runcli, ["func2"])[-1] == runcli.subcommands["func2"]
        assert (
            find_command_chain(runcli, ["func2copy"])[-1]
            == runcli.subcommands["func2copy"]
        )
        assert find_command_chain(runcli, ["name2"])[-1] == runcli.subcommands["name1"]

        with pytest.raises(errors.CommandError):
            find_command_chain(runcli, ["doesnotexist"])
