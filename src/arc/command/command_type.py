from typing import Type, Dict
from arc.utils import symbol
from . import KeywordCommand, PositionalCommand, RawCommand, Command


class CommandType:
    # External Command Type Interface.
    # Doesn't have any direct access to the actual Command Types

    # KeywordCommand - options passed like so: option=value
    KEYWORD = symbol("KEYWORD")

    # PositionalCommand - options passed in order: option1 option2 option3
    POSITIONAL = symbol("POSITIONAL")

    # RawCommand - Doesn't do anything, just passes values along to the command
    RAW = symbol("RAW")

    # Internal Interface, used to map the symbol
    # to the actual Class
    command_type_mappings: Dict[symbol, Type[Command]] = {
        KEYWORD: KeywordCommand,
        POSITIONAL: PositionalCommand,
        RAW: RawCommand,
    }

    @classmethod
    def add_command_type(cls, type_name: str, type_class: Type[Command]):
        """Enables the addition of Custom command classes to modulate Arc's behavior

        :param type_name: the name to be identified with the type. Will be uppercased
            type_name = "test" -> CommandType.TEST

        :param type_class: The Command type class, must inherit from Command
        """
        if not issubclass(type_class, Command):
            raise TypeError("Command Classes MUST inherit from the base Command object")

        setattr(cls, type_name.upper(), symbol(type_name.upper()))
        cls.command_type_mappings[getattr(cls, type_name.upper())] = type_class

    @classmethod
    def get_command_type(cls, command: Command):
        for command_type, command_class in cls.command_type_mappings.items():
            if isinstance(command, command_class) or command is command_class:
                return command_type


def command_factory(name, function, command_type=CommandType.KEYWORD, **kwargs):
    name = name or function.__name__
    type_class = CommandType.command_type_mappings.get(command_type)

    if type_class is None:
        raise AttributeError(f"{command_type} is not a valid Command Type")

    return type_class(name, function, **kwargs)
