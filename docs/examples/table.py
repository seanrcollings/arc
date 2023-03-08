import arc
from arc.present import Table


@arc.command
def command():
    t = Table(["Name", "Age", "Stand"])
    t.add_row(["Jonathen Joestar", 20, "-"])
    t.add_row(["Joseph Joestar", 18, "Hermit Purple (in Part 3)"])
    t.add_row(["Jotaro Kujo", 18, "Star Platinum"])
    t.add_row(["Josuke Higashikata", 16, "Crazy Diamond"])
    t.add_row(["Giorno Giovanna", 15, "Gold Experience"])
    t.add_row(["Joylene Kujo", 19, "Stone Free"])

    arc.print(t)


command()
