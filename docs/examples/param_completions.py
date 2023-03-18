import arc


@arc.command
def command(name: str):
    arc.print(name)


@command.complete("name")
def names(info: arc.CompletionInfo, param: arc.Param):
    yield arc.Completion("Sean")
    yield arc.Completion("Brooke")


command()
