import arc


@arc.command()
def command(state: arc.State):
    # arc.State is a dict-like object, so it can be accessed
    # like a dictionary, or it can be accessed via attributes
    arc.print(state.value)
    arc.print(state["value"])


command(state={"value": 1})
