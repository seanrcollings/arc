from cli import CLI
from cli import Utility

utility = Utility("utility")
cli = CLI(utilities=[utility], context_manager=open("test.txt"))

# @utility.script('example',
#                 options=['print_string', '<int:number>', '<bool:test>'])
# def example(print_string='default', number=4, test=False):
#     '''Here's my doc string'''
#     print(type(print_string), type(number), type(test))
#     print(test)

# @utility.script("read")
# def read(file):
#     print(*file.readlines())


@cli.script("boolean",
            options=['<bool:boolean>', '<ibool:boolean2>', '<sbool:boolean3>'])
def boolean_test(file, boolean3, boolean=False, boolean2=True):
    print(file)


@utility.script("verbose", named_arguements=False)
def verbose(file, *args):
    print(file)
    print(*args)


cli()