from __future__ import annotations
import inspect
import typing as t

import arc
import arc.typing as at
from arc import errors, utils
from arc.core import classful
from arc.autoload import Autoload
from arc.core.alias import AliasDict
from arc.core.app import App
from arc.core.middleware import MiddlewareContainer
from arc.core.middleware.middleware import MiddlewareStack
from arc.decorators import DecoratorMixin, DecoratorStack
from arc.core.documentation import Documentation
from arc.config import config
from arc.autocompletions import CompletionInfo, get_completions, Completion
from arc.core.param import ParamMixin
from arc.core.middleware.exec import DEFAULT_EXEC_MIDDLEWARES
from arc.context import Context

if t.TYPE_CHECKING:
    from .param import ParamDefinition


class Command(ParamMixin, MiddlewareContainer):
    name: str
    parent: Command | None
    subcommands: AliasDict[str, Command]
    param_def: ParamDefinition
    doc: Documentation
    explicit_name: bool
    __autoload__: bool

    def __init__(
        self,
        callback: at.CommandCallback,
        name: str | None = None,
        description: str | None = None,
        parent: Command | None = None,
        explicit_name: bool = True,
        autoload: bool = False,
    ) -> None:
        ParamMixin.__init__(self)
        MiddlewareContainer.__init__(self, [])
        if inspect.isclass(callback):
            self.callback = classful.wrap_class_callback(  # type: ignore
                t.cast(type[at.ClassCallback], callback)
            )
        else:
            self.callback = callback  # type: ignore

        self.name = name or callback.__name__
        self.parent = parent
        self.subcommands = AliasDict()
        self.doc = Documentation(self, description)
        self.explicit_name = explicit_name
        self.__autoload__ = autoload

        if config.environment == "development":
            self.param_def

    __repr__ = utils.display("name")

    def __call__(self, input_args: at.InputArgs = None, state: dict = None) -> t.Any:
        """Entry point for a command, call to execute your command object

        Args:
            input_args (str | list[str], optional): The input you wish to be processed.
                If none is provided, `sys.argv` is used.
            state (dict, optional): Execution State.

        Returns:
            result (Any): The value that the command's callback returns
        """

        app = App(self, config, state=state or {})
        return app(input_args)

    def run(self, ctx: Context):
        stack = MiddlewareStack()
        for command in self.command_chain:
            stack.extend(command.stack)

        ctx = stack.start(ctx)
        args = ctx["arc.args"]

        res = None
        try:
            res = self.callback(**args)
        except Exception as e:
            stack.throw(e)
        else:
            res = stack.close(res)

        return res

    def __completions__(
        self, info: CompletionInfo, *_args, **_kwargs
    ) -> list[Completion]:
        # TODO: it does not take into
        # account that collection types can include more than 1 positional
        # argument.
        global_args, command, command_args = self.split_args(info.words)

        if command is self:
            args = global_args
        else:
            args = command_args

        if not args and command.subcommands:
            return command.__complete_subcommands(info)
        elif info.current.startswith("-"):
            return command.__complete_option(info)
        elif len(args) >= 1 and args[-1].startswith("-"):
            return command.__complete_param_value(info, args[-1].lstrip("-"))
        elif len(args) >= 2 and args[-2].startswith("-"):
            return command.__complete_param_value(info, args[-2].lstrip("-"))
        else:
            if command.is_root and command.subcommands:
                return command.__complete_subcommands(info)
            else:
                return command.__complete_positional_value(info, args)

    def __complete_subcommands(self, info: CompletionInfo) -> list[Completion]:
        return [Completion(command.name) for command in self.subcommands.values()]

    def __complete_option(self, info: CompletionInfo) -> list[Completion]:
        return [Completion(param.cli_name) for param in self.key_params]

    def __complete_param_value(
        self, info: CompletionInfo, param_name: str
    ) -> list[Completion]:
        param = self.get_param(param_name)
        if not param:
            return []

        return get_completions(param, info)

    def __complete_positional_value(
        self, info: CompletionInfo, args: list[str]
    ) -> list[Completion]:
        # TODO: This approach does not take into consideration positonal
        # arguments that are peppered in between options. It only counts ones
        # at the end of the command line.
        pos_arg_count = 0
        for word in reversed(args):
            if word.startswith("-") and word != "--":
                break
            pos_arg_count += 1

        if info.current != "" and pos_arg_count > 0:
            pos_arg_count -= 1

        arg_params = list(self.argument_params)
        if pos_arg_count < len(arg_params):
            param = arg_params[pos_arg_count]
            return get_completions(param, info)

        return []

    @property
    def schema(self) -> dict[str, t.Any]:
        """Schema for the command and all it's subcommands"""
        return {
            "name": self.name,
            "params": [param.schema for param in self.params],
            "subcommands": [com.schema for com in self.subcommands.values()],
        }

    @property
    def is_namespace(self) -> bool:
        """Whether or not this command was created using `arc.namespace()`"""
        return self.callback is namespace_callback

    @property
    def is_root(self) -> bool:
        """Whether or not this command is the root of the command tree"""
        return self.parent is None

    @property
    def root(self) -> "Command":
        """Retrieve the root of the command tree"""
        command = self
        while command.parent:
            command = command.parent

        return command

    @property
    def all_names(self) -> list[str]:
        """A list of all the names that a command may be referred to as"""
        names = [self.name]
        if self.parent:
            names += self.parent.subcommands.aliases_for(self.name)
        return names

    @property
    def command_chain(self) -> list[Command]:
        """Retrieve the chain of commands from root -> self"""
        command = self
        chain = [self]
        while command.parent:
            command = command.parent
            chain.append(command)

        chain.reverse()
        return chain

    # Subcommands ----------------------------------------------------------------

    def subcommand(
        self, name: at.CommandName = None, description: str | None = None
    ) -> t.Callable[[at.CommandCallback], Command]:
        """Create a subcommand of this command

        Args:
            name (at.CommandName, optional): Name(s) of the command.
                Name of the function is used if one is not provided
            description (str | None, optional): Description of the command's functionaly.
                Used in `--help` documentation.
        """

        def inner(callback: at.CommandCallback):
            command_name, aliases = self.get_command_name(callback, name)
            command = Command(
                callback=callback,
                name=command_name,
                description=description,
                parent=self,
            )
            self.add_command(command, aliases)
            return command

        return inner

    def add_command(
        self, command: Command, aliases: t.Sequence[str] | None = None
    ) -> Command:
        """Add a command object as a subcommand

        Args:
            command (Command): The command to add
            aliases (t.Sequence[str] | None, optional): Optional aliases to refter to the command by
        """
        self.subcommands[command.name] = command

        if command.parent is None:
            command.parent = self
            for m in DEFAULT_EXEC_MIDDLEWARES:
                command.stack.try_remove(m)

        if aliases:
            self.subcommands.add_aliases(command.name, *aliases)

        return command

    def add_commands(self, *commands: Command) -> list[Command]:
        """Add multiple commands as subcommands"""
        return [self.add_command(command) for command in commands]

    # Argument Handling ---------------------------------------------------------

    def split_args(self, args: list[str]) -> tuple[list[str], Command, list[str]]:
        """Seperates out a sequence of args into:
        - global arguments
        - a subcommand object
        - command arguments
        """
        index = 0
        global_args: list[str] = []
        while index < len(args) and args[index] not in self.subcommands:
            global_args.append(args[index])
            index += 1

        command: Command = self

        for idx, value in enumerate(args):
            if value in command.subcommands:
                index = idx
                command = command.subcommands.get(value)

        command_args: list[str] = args[index + 1 :]

        return global_args, command, command_args

    # Helpers --------------------------------------------------------------------

    def complete(self, param_name: str):
        param = self.get_param(param_name)
        if param:

            def inner(func: at.CompletionFunc):
                param.comp_func = func  # type: ignore
                return func

            return inner

        raise errors.ParamError(f"No parameter with name: {param_name}")

    def get(self, param_name: str):
        param = self.get_param(param_name)
        if param:

            def inner(func: at.GetterFunc):
                param.getter_func = func  # type: ignore
                return func

            return inner

        raise errors.ParamError(f"No parameter with name: {param_name}")

    def autoload(self, *paths: str):
        Autoload(paths, self, config.autoload_overwrite).load()

    def decorators(self) -> DecoratorStack[at.DecoratorFunc | at.ErrorHandlerFunc]:
        lst = t.cast(list[DecoratorMixin], self.command_chain)
        return DecoratorMixin.create_decostack(lst)

    @staticmethod
    def get_command_name(
        callback: at.CommandCallback, names: at.CommandName
    ) -> tuple[str, tuple[str, ...]]:
        if names is None:
            name = callback.__name__

            if config.transform_snake_case:
                name = name.replace("_", "-")

            return name, tuple()

        if isinstance(names, str):
            return names, tuple()

        return names[0], tuple(names[1:])


def namespace_callback(ctx: Context):
    arc.usage(ctx.command)
