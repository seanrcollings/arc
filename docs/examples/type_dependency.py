import arc


class Dependency:
    def __init__(self, value: int) -> None:
        self.value = value

    @classmethod
    def __depends__(cls, ctx: arc.Context):
        return Dependency(2)


@arc.command()
def command(dep: Dependency):
    arc.print(dep)
    arc.print(dep.value)


command()
