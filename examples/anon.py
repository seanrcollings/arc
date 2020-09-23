from arc import CLI, Utility

util = Utility("util")
cli = CLI(utilities=[util])


@util.script("anon", options=["name"])
def util_anon(name):
    print(name)


@cli.script("anon", options=["name"])
def cli_anon(name):
    print(name)


cli()
