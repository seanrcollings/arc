import arc


class TestCommandExtension:
    def test_command_extension(self):
        @arc.command(value=2)
        def command():
            ...

        assert command.data == {"value": 2}

    def test_subcommand_extension(self):
        @arc.command
        def command():
            ...

        @command.subcommand(value=2)
        def sub():
            ...

        assert sub.data == {"value": 2}


def test_parameter_extension():
    @arc.command
    def command(val: int = arc.Argument(value=2)):
        ...

    param = [p for p in command.params if p.argument_name == "val"][0]
    assert param.data == {"value": 2}
