import arc


class ContextManager:
    def __init__(self, value) -> None:
        self.value = value

    def __enter__(self):
        arc.print("Entering the Context")
        return self

    def __exit__(self, *args):
        arc.print("Exiting the Context")

    @classmethod
    def __convert__(cls, value):
        return cls(value)


@arc.command
def command(val: ContextManager):
    arc.print(val)


command()
