import pytest
from arc import CLI, errors, config


def test_transform(cli: CLI):
    @cli.subcommand()
    def two_words(*, first_name: str = "", other_arg: str = ""):
        return first_name

    assert cli("two-words --first-name sean") == "sean"
    assert cli("two-words --first-name sean --other-arg hi") == "sean"

    with pytest.raises(errors.CommandNotFound):
        cli("two_words")

    with pytest.raises(errors.UsageError):
        cli("two-words --first_name sean")


def test_disable_transform(cli: CLI):
    try:
        config.transform_snake_case = False

        @cli.subcommand()
        def two_words(*, first_name: str = "", other_arg: str = ""):
            return first_name

        assert cli("two_words --first_name sean") == "sean"
        assert cli("two_words --first_name sean --other_arg hi") == "sean"

        with pytest.raises(errors.CommandNotFound):
            cli("two-words")

        with pytest.raises(errors.UsageError):
            cli("two_words --first-name sean --other-arg hi")
    finally:
        config.transform_snake_case = True