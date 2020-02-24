'''Base CLI example'''
from arc import CLI, Utility
from arc.utilities import debug

cli = CLI(utilities=[debug])

cli()
