from __future__ import annotations
import functools
import inspect
import typing as t

import arc
import arc.typing as at
from arc import errors, utils
from arc.define import classful
from arc.autoload import Autoload
from arc.define.alias import AliasDict
from arc.define.documentation import Documentation
from arc.config import config
from arc.autocompletions import CompletionInfo, get_completions, Completion
from arc.define.param import ParamMixin
from arc.context import Context
from arc.runtime import App, MiddlewareContainer, MiddlewareStack, ExecMiddleware

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
            self.callback = self.wrap_class_callback(  # type: ignore
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
        ctx.logger.debug("Executing: %s", self)
        stack = MiddlewareStack()
        for command in self.command_chain:
            stack.extend(command.stack)

        ctx = stack.start(ctx)
        if "arc.args" not in ctx:
            raise errors.InternalError(
                "The command's arguments were not set during execution "
                "(ctx['arc.args] is not set). This likely means there "
                "is a problem with your middleware stack"
            )

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
        return []
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

    @t.overload
    def subcommand(
        self,
        /,
        command: Command,
        *aliases: str,
    ) -> Command:
        ...

    @t.overload
    def subcommand(
        self,
        /,
        callback: at.CommandCallback,
    ) -> Command:
        ...

    @t.overload
    def subcommand(
        self, /, name: str | None = None, *aliases: str, desc: str | None = None
    ) -> t.Callable[[at.CommandCallback], Command]:
        ...

    def subcommand(self, first=None, *aliases, desc=None):
        """Create a new child commmand of this command OR
        adopt a already created command as the child.

        ```py
        @command.subcommand("name1", "alias", desc="...")
        def subcommand():
            ...
        ```
        OR
        ```py
        @arc.command("name1")
        def subcommand():
            ...

        command.subcommand(subcommand, "alias", desc="...")
        ```

        """

        if isinstance(first, type(self)):
            self.add_command(first, aliases)
        else:

            def inner(callback: at.CommandCallback):
                command_name = self.get_canonical_subcommand_name(callback, first)
                command = Command(
                    callback=callback,
                    name=command_name,
                    description=desc,
                    parent=self,
                )
                self.add_command(command, aliases)
                return command

            if callable(first):
                callback = first
                first = None
                return inner(callback)
            elif first is None or isinstance(first, str):
                return inner
            else:
                raise errors.CommandError(
                    "Bad input to command.subcommand(). "
                    "Needs to be used as a decorator, or "
                    "passed an already construction Command insance"
                )

    def add_command(
        self, command: Command, aliases: t.Sequence[str] | None = None
    ) -> Command:
        """Add a command object as a subcommand

        Args:
            command (Command): The command to add
            aliases (t.Sequence[str] | None, optional): Optional aliases to refter to the command by
        """
        if command is self:
            raise errors.CommandError(
                "Command cannot be added as children of themselves"
            )

        self.subcommands[command.name] = command

        if command.parent is None:
            command.parent = self
            for m in ExecMiddleware.all():
                command.stack.try_remove(m)

        if aliases:
            self.subcommands.add_aliases(command.name, *aliases)

        return command

    def add_commands(self, *commands: Command) -> list[Command]:
        """Add multiple commands as subcommands"""
        return [self.add_command(command) for command in commands]

    @staticmethod
    def get_canonical_subcommand_name(
        callback: at.CommandCallback,
        cannonical_name: str | None,
    ) -> str:
        if cannonical_name is None:
            cannonical_name = callback.__name__

            if config.transform_snake_case:
                cannonical_name = cannonical_name.replace("_", "-")

        return cannonical_name

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

    @staticmethod
    def wrap_class_callback(cls: type[at.ClassCallback]):
        if not hasattr(cls, "handle"):
            raise errors.CommandError("class-style commands require a handle() method")

        def wrapper(**kwargs):
            inst = cls()
            for key, value in kwargs.items():
                setattr(inst, key, value)

            return cls.handle(inst)

        classful.class_signature(cls)
        functools.update_wrapper(wrapper, cls)
        return wrapper


@t.overload
def command(callback: at.CommandCallback, /) -> Command:
    ...


@t.overload
def command(
    name: str | None = None, /, *, desc: str | None = None
) -> t.Callable[[at.CommandCallback], Command]:
    ...


def command(
    first: at.CommandCallback | str | None = None, /, *, desc: str | None = None
):
    """Create an arc Command

    ```py
    @arc.command
    def command():
        print("Hello there!")
    ```

    Args:
        name (str | None, optional): The name for this command.
            If one is not provided, the function's name will be used.
        desc (str | None, optional): Description for the command. If
            one is not provided, the docstring description will be used
    """

    name = None

    def inner(callback: at.CommandCallback) -> Command:
        command = Command(
            callback=callback,
            name=Command.get_canonical_subcommand_name(callback, name),
            description=desc,
            parent=None,
            explicit_name=bool(name),
            autoload=True,
        )
        command.use(ExecMiddleware.all())
        return command

    if isinstance(first, str) or first is None:
        name = first
        return inner
    else:
        return inner(first)


def namespace(name: str, *, desc: str | None = None) -> Command:
    """Create an arc Command, that is not executable on it's own,
    but can have commands nested underneath it.

    ```py
    ns = arc.namespace("ns")

    @ns.subcommand
    def sub():
        print("I'm a subcommand")
    ```

    Args:
        name (str): Name of the command
        desc (str | None, optional): Description for the command.

    Returns:
        command: A command object without a callback associated with it
    """
    command = Command(
        callback=namespace_callback,
        name=name,
        description=desc,
        parent=None,
        autoload=True,
    )
    command.use(ExecMiddleware.all())
    return command


def namespace_callback(ctx: Context):
    arc.usage(ctx.command)
    arc.exit(1)
