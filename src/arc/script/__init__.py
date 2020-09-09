from arc._utils import symbol
from .keyword_script import KeywordScript
from .positional_script import PositionalScript
from .raw_script import RawScript


class ScriptType:
    KEYWORD = symbol("KEYWORD")
    POSITIONAL = symbol("POSITIONAL")
    RAW = symbol("RAW")


def script_factory(name, function, script_type=ScriptType.KEYWORD):
    name = name if name else function.__name__

    # KeywordScript - options passed like so: option=value
    if script_type is ScriptType.KEYWORD:
        return KeywordScript(name, function)

    # PositionalScript - options passed in order: option1 option2 option3
    elif script_type is ScriptType.POSITIONAL:
        return PositionalScript(name, function)

    # RawScript - Doesn't do anything, just passes values along to the script
    else:
        return RawScript(name, function)
