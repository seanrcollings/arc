import pytest
import arc


def test_basic():
    @arc.command
    class command:
        def handle(self):
            return True

    assert command("") is True


def test_no_handle():
    with pytest.raises(arc.errors.CommandError):

        @arc.command
        class command:
            ...


def test_arguments():
    @arc.command
    class command:
        val: int
        opt: int = arc.Option()
        flag: bool = arc.Flag()

        def handle(self):
            return (self.val, self.opt, self.flag)

    assert command("1 --opt 2 --flag") == (1, 2, True)


def test_other_methods():
    @arc.command
    class command:
        val: int

        def handle(self):
            return self.helper()

        def helper(self):
            return self.val

    assert command("1") == 1
