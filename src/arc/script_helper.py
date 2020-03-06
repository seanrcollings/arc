from arc.errors import ExecutionError, ArcError
from arc.__option import Option
from arc import Config


# BUILDERS
def build_options(options: list) -> dict:
    '''Creates option objects'''
    if options is None:
        return {}

    built_options = {}
    for option in options:
        option_obj = Option(option)
        built_options[option_obj.name] = option_obj
    return built_options


def build_flags(flags: list) -> dict:
    '''Insures flags follow specific standards
        :param flags: list of all flags registered to the scriot

        :returns: dictionary of flag names paired with a default False value
    '''
    if flags is None:
        return {}

    built_flags = {}
    for flag in flags:
        if not flag.startswith(Config.flag_denoter):
            raise ArcError(
                "Flags must start with the denoter",
                f"'{Config.flag_denoter}'",
                "\nThis denoter can be changed by editing 'Config.flag_denoter'"
            )
        built_flags[flag.lstrip(Config.flag_denoter)] = False

    return built_flags


# Other helper functions
def split_on_sep(options: list, sep: str):
    '''Generator that splits strings based on a provided seperator'''

    for option in options:
        if sep not in option:
            raise ExecutionError("Options must be seperated",
                                 f"from their values by '{sep}'")
        if option.endswith(sep):
            raise ExecutionError("Options must be given a value")

        name, value = option.split(sep)
        yield (name, value)
