import logging
import arc


@arc.command()
def command(*, verbose: bool):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)


@command.subcommand()
def sub():
    logging.info("This is an info message")
    logging.debug("This is a debug message")


command()
