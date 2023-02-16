import pytest
from arc import errors
import arc


def test_transform():
    command = arc.namespace("command")

    @command.subcommand()
    def two_words(*, first_name: str = "", other_arg: str = ""):
        return first_name

    assert command("two-words --first-name sean") == "sean"
    assert command("two-words --first-name sean --other-arg hi") == "sean"

    with pytest.raises(errors.UnrecognizedArgError):
        command("two_words")

    with pytest.raises(errors.UnrecognizedArgError):
        command("two-words --first_name sean")


def test_disable_transform():
    try:
        arc.configure(transform_snake_case=False)

        command = arc.namespace("command")

        @command.subcommand()
        def two_words(*, first_name: str = "", other_arg: str = ""):
            return first_name

        assert command("two_words --first_name sean") == "sean"
        assert command("two_words --first_name sean --other_arg hi") == "sean"

        with pytest.raises(errors.UnrecognizedArgError):
            command("two-words")

        with pytest.raises(errors.UnrecognizedArgError):
            command("two_words --first-name sean --other-arg hi")
    finally:
        arc.configure(transform_snake_case=True)


def test_explicit_names():
    command = arc.namespace("command")

    @command.subcommand("two_words")
    def two_words(
        *,
        first_name: str = arc.Option(name="first_name"),
        other_arg: str = arc.Option(name="other_arg")
    ):
        return first_name

    assert command("two_words --first_name sean --other_arg hi") == "sean"
