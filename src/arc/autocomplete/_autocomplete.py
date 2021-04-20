from dataclasses import dataclass

from arc.command import Command
from arc.parser import parse, CommandNode
from arc import arc_config

from . import utils


@dataclass
class Completion:
    value: str
    description: str

    def __str__(self):
        return f"{self.value}\t{self.description}"


class AutoComplete:
    def __init__(self, cli: Command, command_str: str):
        self.cli = cli
        # if the first token is the name of the tool, we
        # can just discard it
        self.command_str = command_str.lstrip(self.cli.name).lstrip(" ")
        self.completions: list[Completion] = []

        if self.command_str in ("", " "):
            self.suggest_subcommands = True
            self.node = CommandNode([], [])
            self.namespace: list[str] = []
            self.command = self.cli
        else:
            self.suggest_subcommands = self.command_str[-1] != " "
            self.command_str = self.command_str.strip()
            self.node = parse(self.command_str)
            self.namespace, self.command = utils.current_namespace(
                self.cli, self.node.namespace
            )

    def complete(self):
        self.complete_arguments()
        self.complete_subcommands()

    def complete_arguments(self):
        for name, option in self.command.args.items():
            if name not in [arg.name for arg in self.node.args]:
                if option.annotation == bool:
                    self.completions.append(
                        Completion(f"{arc_config.flag_denoter}{name}", "FLAG")
                    )
                else:
                    self.completions.append(
                        Completion(
                            f"{name}{arc_config.arg_assignment}",
                            option.annotation.__name__,
                        )
                    )

    def complete_subcommands(self):
        if (
            len(self.node.args) == 0 and self.suggest_subcommands
        ) or self.command == self.cli:

            for name, subcommand in self.command.subcommands.items():
                if name not in ("_autocomplete", "help"):
                    sep = arc_config.namespace_sep
                    name = (
                        f"{sep.join(self.namespace)}{sep}{name}"
                        if len(self.namespace) > 0
                        else name
                    )
                    doc = (
                        subcommand.doc.split("\n")[0]
                        if subcommand.doc is not None
                        else ""
                    )
                    self.completions.append(Completion(name, doc))
