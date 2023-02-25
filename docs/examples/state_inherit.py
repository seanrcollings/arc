import arc


class MyState(arc.State):
    name: str

    def punch(self):
        arc.print(f"ORA ORA, {self.name}")


@arc.command
def punch(state: MyState):
    state.punch()


punch(state={"name": "DIO"})
