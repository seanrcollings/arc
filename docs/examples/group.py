import arc


@arc.group
class MyGroup:
    firstname: str
    reverse: bool


@arc.command
def hello(group: MyGroup):
    if group.reverse:
        group.firstname = group.firstname[::-1]

    arc.print(f"Hello, {group.firstname}! Hope you have a wonderful day!")


hello()
