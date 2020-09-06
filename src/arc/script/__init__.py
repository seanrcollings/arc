from .keyword_script import KeywordScript
from .positional_script import PositionalScript
from .raw_script import RawScript


def script_factory(name, function, positional=False):
    name = name if name else function.__name__
    # KeywordScript - options passed like so: option=value
    #   VarKeyworkScript? - for **kwargs
    if not positional:
        return KeywordScript(name, function)

    # PositionalScript - options passed in order: option1 option2 option3
    #   PositionalKeyWordScript? - for *args
    if positional:
        return PositionalScript(name, function)

    # RawScript - Doesn't do anything, just passes values along to the script
    return RawScript(name, function)

