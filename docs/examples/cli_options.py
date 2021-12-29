import arc

cli = arc.CLI()


@cli.command()
def command(state: arc.State):
    if state.verbose:
        print("--------- Verbose Mode ---------------")

    print("hi there")


@cli.options
def options(*, verbose: bool, ctx: arc.Context):
    ctx.state.verbose = verbose


cli()
