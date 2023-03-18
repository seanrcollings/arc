from typing import Literal
import pytest

import arc
from arc import autocompletions


@pytest.mark.parametrize(
    "info",
    [
        autocompletions.CompletionInfo([], ""),
        autocompletions.CompletionInfo(["sub"], "sub"),
    ],
)
def test_subcommand_completions(info: autocompletions.CompletionInfo):
    @arc.command
    def command():
        ...

    @command.subcommand
    def sub1():
        """Desc 1"""

    @command.subcommand
    def sub2():
        """Desc 2"""

    res = autocompletions.get_completions(command, info)
    assert res == [
        autocompletions.Completion("sub1", "Desc 1"),
        autocompletions.Completion("sub2", "Desc 2"),
    ]


def test_argument_completions():
    @arc.command
    def command(name: Literal["Johnathen", "Joseph"]):
        ...

    info = autocompletions.CompletionInfo([], "")
    assert autocompletions.get_completions(command, info) == [
        autocompletions.Completion("Johnathen"),
        autocompletions.Completion("Joseph"),
    ]


def test_option_name_completions():
    @arc.command
    def command(*, option: str, flag: bool):
        ...

    info = autocompletions.CompletionInfo(["-"], "-")
    assert autocompletions.get_completions(command, info) == [
        autocompletions.Completion("--help", command.get_param("help").description),
        autocompletions.Completion("--option"),
        autocompletions.Completion("--flag"),
    ]


def test_option_value_completions():
    @arc.command
    def command(*, name: Literal["Johnathen", "Joseph"]):
        ...

    info = autocompletions.CompletionInfo(["--name"], "")
    assert autocompletions.get_completions(command, info) == [
        autocompletions.Completion("Johnathen"),
        autocompletions.Completion("Joseph"),
    ]


def test_custom_completions():
    @arc.command
    def command(name: str):
        ...

    @command.complete("name")
    def names(info, param):
        yield autocompletions.Completion("Johnathen")
        yield autocompletions.Completion("Joseph")

    info = autocompletions.CompletionInfo([], "")
    assert autocompletions.get_completions(command, info) == [
        autocompletions.Completion("Johnathen"),
        autocompletions.Completion("Joseph"),
    ]
