from arc.utils.exceptions import handle
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

    return cli


class TestRunFunction:
    def test_success(self, runcli: CLI):
        run(runcli, "ok") == Ok()
        run(runcli, "err") == Err()
        run(runcli, "func1 x=hi") == Ok("hi")
        run(runcli, "func2 x=2") == Ok(2)

    def test_failure(self, runcli: CLI):
        with pytest.raises(errors.ValidationError):
            run(runcli, "func1")

        with pytest.raises(errors.CommandError):
            run(runcli, "func2 x=string")

    def test_handle_exception(self, runcli: CLI):
        config.mode = "production"
        with pytest.raises(SystemExit):
            run(runcli, "func1", handle_exception=True)

        with pytest.raises(SystemExit):
            run(runcli, "func2 x=string", handle_exception=True)

    def test_check_result(self, runcli: CLI):
        run(runcli, "func1 x=hi", check_result=True) == "hi"
        run(runcli, "func2 x=2", check_result=True) == 2

        config.mode = "production"
        with pytest.raises(errors.ExecutionError):
            run(runcli, "err", check_result=True)

        with pytest.raises(SystemExit):
            run(runcli, "err", check_result=True, handle_exception=True)


class TestGetCommandNamespace:
    command = "command"
    command_args = ["name=sean", "--flag"]
    args = [command, *command_args]

    def test_empty(self):
        assert get_command_namespace([]) == ([], [])

    def test_no_namespace(self):
        assert get_command_namespace(self.command_args) == ([], self.command_args)

    def test_single(self):
        assert get_command_namespace(self.args) == ([self.command], self.command_args)

    def test_nested(self):
        nested = "nested:command:name"
        assert get_command_namespace([nested, *self.command_args]) == (
            nested.split(":"),
            self.command_args,
        )


class TestFindCommand:
    def test_find(self, cli: CLI):
        @cli.subcommand(("name1", "name2"))
        def _():
            ...

        assert find_command(cli, ["func1"])[0] == cli.subcommands["func1"]
        assert find_command(cli, ["func2"])[0] == cli.subcommands["func2"]
        assert find_command(cli, ["func2copy"])[0] == cli.subcommands["func2copy"]
        assert find_command(cli, ["name2"])[0] == cli.subcommands["name1"]

        with pytest.raises(errors.CommandError):
            find_command(cli, ["doesnotexist"])
