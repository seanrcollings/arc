from dataclasses import dataclass

from arc.command import Command
from arc.parser import parse, CommandNode

from . import utils


@dataclass
class Completion:
    value: str
    description: str

    def __str__(self):
        return f"{self.value}\t{self.description}"


class AutoComplete:
    def __init__(self, cli: Command, tokens: list[str]):
        self.cli = cli
        # if the first token is the name of the tool, we
        # can just discard it
        self.tokens = tokens[1:] if tokens[0] == self.cli.name else tokens
        self.completions: list[Completion] = []
        if utils.is_empty(self.tokens):
            self.ends_in_space = False
            self.node = CommandNode([], [])
            self.namespace: list[str] = []
            self.command = self.cli
        else:
            self.ends_in_space = self.tokens[-1][-1] == " "
            self.tokens[-1] = self.tokens[-1].strip()
            self.node = parse(list(self.tokens))
            self.namespace, self.command = utils.current_namespace(
                self.cli, self.node.namespace
            )

    def complete(self):
        self.complete_arguments()
        self.complete_subcommands()

    def complete_arguments(self):
        for name, option in self.command.args.items():
            if option.annotation == bool:
                self.completions.append(Completion(f"--{name}", "FLAG"))
            else:
                self.completions.append(
                    Completion(f"{name}=", option.annotation.__name__)
                )

    def complete_subcommands(self):
        if (
            len(self.node.args) == 0 and not self.ends_in_space
        ) or self.command == self.cli:
            for name, subcommand in self.command.subcommands.items():
                if name in ("_autocomplete", "help"):
                    continue

                name = (
                    f"{':'.join(self.namespace)}:{name}"
                    if len(self.namespace) > 0
                    else name
                )
                self.completions.append(Completion(name, subcommand.doc or ""))
