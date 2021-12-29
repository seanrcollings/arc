import arc

ns = arc.namespace("ns")


@ns.subcommand()
def sub():
    print("Namespace Example")
