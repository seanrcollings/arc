import sys
import io
from arc import color, CLI


def test_colorize():
    colored = color.colorize("test", color.fg.RED)
    assert colored.startswith(str(color.fg.RED))
    assert colored.endswith(str(color.effects.CLEAR))

    colored = color.colorize("test", color.fg.RED, clear=False)
    assert colored.startswith(str(color.fg.RED))
    assert not colored.endswith(str(color.effects.CLEAR))


# Because StringIO is not terminal-like, escape-sequnces will be removed
def test_output(cli: CLI):
    try:
        stdout = sys.stdout
        fake = io.StringIO()
        sys.stdout = fake

        @cli.command()
        def test():
            print(f"{color.fg.GREEN}green!{color.effects.CLEAR}")

        cli("test")

        fake.seek(0)
        assert fake.read() == "green!\n"

    finally:
        sys.stdout = stdout
