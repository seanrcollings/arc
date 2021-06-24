from typing import _SpecialForm as SpecialForm
from . import converter_mapping


def base_input_func(prompt: str, converter):
    user_input = input(prompt)
    return converter().convert(user_input)


# Dynamicaly creates a function for each of the converters
# defined in Config.converters.
for kind, converter in converter_mapping.items():
    if isinstance(kind, SpecialForm):
        continue

    globals()[f"input_to_{kind.__name__}"] = lambda p, c=converter: base_input_func(
        p, c
    )
