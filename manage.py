from app import cli
from app.utility import Utility

utility = Utility("utility")
cli.register_utilities(utility)


@utility.script('example',
                options=['print_string', '<int:number>', '<bool:test>'])
def example(print_string='default', number=4, test=False):
    '''Here's my doc string'''
    print(type(print_string), type(number), type(test))
    print(test)


@cli.script("boolean",
            options=['<bool:boolean>', '<ibool:boolean2>', '<sbool:boolean3>'])
def boolean_test(boolean3, boolean=False, boolean2=True):
    print(type(boolean), type(boolean2), type(boolean3))
    print(boolean, boolean2, boolean3)


cli()