from arc import CLI
from cli_command import command
from cli_namespace import ns

cli = CLI()
cli.install_commands(command, ns)

# Could also place any commands you wanted in here :)


cli()
