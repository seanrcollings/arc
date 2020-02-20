from cli import CLI
from cli import Utility
from cli.utilities import files

cli = CLI()
cli.install_utilities(files)

cli()