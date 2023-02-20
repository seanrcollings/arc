import arc

ns = arc.namespace("ns")


@ns.subcommand()
def sub():
    arc.print("Namespace Example")


ns()
