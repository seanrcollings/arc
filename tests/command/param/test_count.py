import arc


def test_count():
    @arc.command()
    def command(flag: int = arc.Count()):
        return flag

    assert command("") == 0
    assert command("--flag --flag --flag") == 3
