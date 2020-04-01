from arc import CLI, Utility

util = Utility("util")
cli = CLI(utilities=[util])


@util.script("no_args")
def util_no_args():
    print("util no_args here!")


@util.script("anon", options=["name"])
def util_anon(name):
    print(name)


@cli.script("no_args")
def cli_no_args():
    print("no_args here!")


@cli.script("anon", options=["name"])
def cli_anon(name):
    print(name)


cli()