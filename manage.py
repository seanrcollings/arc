import logging
from arc import CLI, Utility

ut = Utility("test")
cli = CLI(utilities=[ut])

# logging.debug('This is a debug message')
# logging.info('This is an info message')
# logging.warning('This is a warning message')
# logging.critical('This is a critical message')


@ut.script("greet", options=["name"])
def greet(name="Jotaro Kujo"):
    '''Command that greets someone CLI command'''
    print(f"Hello, {name}!")


cli()
