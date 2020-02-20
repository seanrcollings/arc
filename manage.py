from arc import CLI


def greet(name="Jotaro Kujo"):
    '''Command that greets someone CLI command'''
    print(f"Hello, {name}!")
    print(f"This command is associated witht the global CLI")


scripts = {
    "greet": {
        "function": greet,
        "options": ["name"],
        "named_arguements": True
    }
}

cli = CLI(scripts=scripts)

cli()