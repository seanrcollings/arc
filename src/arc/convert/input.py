from arc import config


def base_input_func(prompt: str, converter):
    user_input = input(prompt)
    return converter().convert_wrapper(user_input)


# Dynamicaly creates a function for each of the converters
# defined in Config.converters.
for name, converter in config.converters.items():
    globals()[f"input_to_{name}"] = lambda p, c=converter: base_input_func(p, c)
