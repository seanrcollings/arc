from typing import Type
from arc.utils import symbol
from .script import Script
from .keyword_script import KeywordScript
from .positional_script import PositionalScript
from .raw_script import RawScript
from .legacy_script import LegacyScript


class ScriptType:
    # External Script Type Interface.
    # Doesn't have any direct access to thes Script Types

    # KeywordScript - options passed like so: option=value
    KEYWORD = symbol("KEYWORD")

    # PositionalScript - options passed in order: option1 option2 option3
    POSITIONAL = symbol("POSITIONAL")

    # LegacyScript - legacy implementation of script object
    LEGACY = symbol("LEGACY")

    # RawScript - Doesn't do anything, just passes values along to the script
    RAW = symbol("RAW")

    # Internal Interface, used to map the symbol
    # to the actual Class
    script_type_mappings = {
        KEYWORD: KeywordScript,
        POSITIONAL: PositionalScript,
        LEGACY: LegacyScript,
        RAW: RawScript,
    }

    @classmethod
    def add_script_type(cls, type_name: str, type_class: Type[Script]):
        """Enables the addition of Custom script classes to modulate Arc's behavior

        :param type_name: the name to be identified with the type. Will be uppercased
            type_name = "test" -> ScriptType.TEST

        :param type_class: The Script type class, must inherit from Script
        """
        if not issubclass(type_class, Script):
            raise TypeError("Script Classes MUST inherit from the base Script object")

        setattr(cls, type_name.upper(), symbol(type_name.upper()))
        cls.script_type_mappings[getattr(cls, type_name.upper())] = type_class


def script_factory(name, function, script_type=ScriptType.KEYWORD, **kwargs):
    name = name if name else function.__name__
    type_class = ScriptType.script_type_mappings.get(script_type)

    if type_class is None:
        raise AttributeError(f"{script_type} is not a valid Script Type")

    return type_class(name, function, **kwargs)
