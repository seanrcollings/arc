import arc


@arc.group
class Group:
    name: str

    def pre_exec(self):
        arc.print("Before the command executes")

    def post_exec(self):
        arc.print("After the command executes")


@arc.command
def command(group: Group):
    arc.print(f"Hello, {group.name}")


command()
