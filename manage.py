from arc import CLI, Utility

ut = Utility("test")
cli = CLI(utilities=[ut])

# @ut.script("greet", options=["name"])
# def greet(name="Jotaro Kujo"):
#     '''Command that greets someone CLI command'''
#     print(f"Hello, {name}!")
#     print(f"This command is associated witht the global CLI")

cli()
