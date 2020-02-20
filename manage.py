from arc import CLI
from arc import Utility
from arc.utilities import files

cli = CLI()
cli.install_utilities(files)

cli()