from app.cli import CLI

from app.utility import Utility
utility = Utility("utility")
cli = CLI(utilities=[utility])


@utility.script('example', options=['print_string', '<int:number>', '<bool:test>'])
def example(print_string='default', number=4, test=False):
    '''
    Here's my doc string
    '''
    print(type(print_string), type(number), type(test))
    print(test)




cli()