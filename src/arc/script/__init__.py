from arc._utils import symbol
from .keyword_script import KeywordScript
from .positional_script import PositionalScript
from .raw_script import RawScript
from .legacy_script import LegacyScript


class ScriptType:
    KEYWORD = symbol("KEYWORD")
    POSITIONAL = symbol("POSITIONAL")
    LEGACY = symbol("LEGACY")
    RAW = symbol("RAW")


def script_factory(name, function, script_type=ScriptType.KEYWORD, **kwargs):
    name = name if name else function.__name__

    # KeywordScript - options passed like so: option=value
    if script_type is ScriptType.KEYWORD:
        return KeywordScript(name, function, **kwargs)

    # PositionalScript - options passed in order: option1 option2 option3
    elif script_type is ScriptType.POSITIONAL:
        return PositionalScript(name, function, **kwargs)

    # LegacyScript - legacy implementation of script object
    elif script_type is ScriptType.LEGACY:
        return LegacyScript(name, function, **kwargs)

    # RawScript - Doesn't do anything, just passes values along to the script
    elif script_type is ScriptType.RAW:
        return RawScript(name, function, **kwargs)

    else:
        raise AttributeError(f"{script_type} is not a valid Script Type")
