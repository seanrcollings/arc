from __future__ import annotations
from datetime import datetime

import functools
import inspect
import sys
import typing as t

import arc
from arc.config import Config
import arc.typing as at
from arc import api, color, errors
from arc.autocompletions import Completion, CompletionInfo, get_completions
from arc.define import classful
from arc.define.alias import AliasDict
from arc.define.documentation import Documentation
from arc.define.param import ParamMixin
from arc.present.joiner import Join
from arc.runtime import App, ExecMiddleware, MiddlewareManager, MiddlewareStack
from arc.runtime import Context

if t.TYPE_CHECKING:
    from .param import ParamDefinition


class Command(ParamMixin, MiddlewareManager):
    name: str
    parent: Command | None
    config: Config
    subcommands: AliasDict[str, Command]
    param_def: ParamDefinition
    doc: Documentation
    explicit_name: bool
    data: dict[str, t.Any]

    def __init__(
        self,
        callback: at.CommandCallback,
        config: Config,
        name: str | None = None,
        description: str | None = None,
        parent: Command | None = None,
        explicit_name: bool = True,
        autoload: bool = False,
        **kwargs: t.Any,
    ) -> None:
        ParamMixin.__init__(self)
        MiddlewareManager.__init__(self, [])
        if inspect.isclass(callback):
            self.callback = self.wrap_class_callback(
                t.cast(type[at.ClassCallback], callback)
            )
        else:
            self.callback = callback

        self.config = config
        self.name = name or callback.__name__
        self.parent = parent
        self.subcommands = AliasDict()
        self.doc = Documentation(self, self.config.present, description)
        self.explicit_name = explicit_name
        self.data = kwargs

    __repr__ = api.display("name")

    def __call__(
        self, input_args: at.InputArgs = None, state: dict[str, t.Any] = None
    ) -> t.Any:
        """Entry point for a command, call to execute your command object

        Args:
            input_args (str | list[str], optional): The input you wish to be processed.
                If none is provided, `sys.argv` is used.
            state (dict, optional): Execution State.

        Returns:
            result (Any): The value that the command's callback returns
        """

        app = App(self, state=state or {})
        return app(input_args)

    def __iter__(self) -> t.Iterator[Command]:
        stack: list[Command] = []
        stack.append(self)

        while stack:
            curr = stack.pop()
            stack.extend(curr.subcommands.values())
            yield curr

    def __completions__(self, info: CompletionInfo) -> t.Iterable[Completion]:
        # TODO: This is a very naive approach it:
        # - does not take into account that collection
        #   types can include more than 1 positional argument.
        # - Does not take into account that collection types
        #   can be repeated when they're options
        # - Assumes that the user's cursor is at the end of the line
        command, args = self.find_command(info.words)

        if len(args) == 0:
            yield from command.__complete_subcommands(info)
            yield from command.__complete_positional_value(info, args)
        elif info.current.startswith("-"):
            yield from command.__complete_options(info)
        elif args[-1].startswith("-"):
            name = args[-1].lstrip("-")
            param = command.get_param(name)
            if not param:
                return
            if param.is_flag:
                yield from command.__complete_positional_value(info, args)
            else:
                yield from command.__complete_param_value(info, name)
        else:
            pos = command.__complete_positional_value(info, args)
            if pos:
                yield from pos
            elif len(args) == 1 and any(
                c.name.startswith(args[0]) for c in self.subcommands.values()
            ):
                yield from command.__complete_subcommands(info)

    def __complete_subcommands(self, info: CompletionInfo) -> t.Iterable[Completion]:
        for command in self.subcommands.values():
            yield Completion(command.name, description=command.doc.short_description)

    def __complete_options(self, info: CompletionInfo) -> t.Iterable[Completion]:
        for param in self.key_params:
            yield Completion(param.cli_name, description=param.description)

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
        # TODO: This approach does not take into consideration positional
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

    def run(self, ctx: Context) -> t.Any:
        start_time: datetime | None = ctx.get("arc.debug.start")
        if start_time:
            diff = datetime.now() - start_time
            ctx.logger.debug(f"Executing: {self} ({diff.total_seconds():.4f}s)")
        else:
            ctx.logger.debug(f"Executing: {self}")

        stack = MiddlewareStack()
        for command in self.command_chain:
            stack.extend(command._stack)

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

    # Subcommands ----------------------------------------------------------------

    @t.overload
    def subcommand(
        self,
        /,
        first: Command,
        *aliases: str,
    ) -> Command:
        ...

    @t.overload
    def subcommand(
        self,
        /,
        first: at.CommandCallback,
    ) -> Command:
        ...

    @t.overload
    def subcommand(
        self,
        /,
        first: str | None = None,
        *aliases: str,
        desc: str | None = None,
        **kwargs: t.Any,
    ) -> t.Callable[[at.CommandCallback], Command]:
        ...

    def subcommand(
        self,
        /,
        first: t.Any = None,
        *aliases: str,
        desc: str | None = None,
        **kwargs: t.Any,
    ) -> Command | t.Callable[[at.CommandCallback], Command]:
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
            return first
        else:

            def inner(callback: at.CommandCallback) -> Command:
                command_name = self.get_canonical_subcommand_name(
                    callback, first, self.config.transform_snake_case
                )

                command = Command(
                    callback=callback,
                    name=command_name,
                    description=desc,
                    config=self.config,
                    parent=self,
                    **kwargs,
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
                    "passed an already constructed Command insance"
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
                command._stack.try_remove(m)

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
        transform_snake_case: bool = True,
    ) -> str:

        if cannonical_name is None:
            cannonical_name = callback.__name__

            if transform_snake_case:
                cannonical_name = cannonical_name.replace("_", "-")

        return cannonical_name

    # Helpers --------------------------------------------------------------------

    def find_command(self, names: list[str]) -> tuple[Command, list[str]]:
        """Seperates out a sequence of args into:
        - a subcommand object
        - command arguments
        """
        index = 0
        command: Command = self

        for name in names:
            if name in command.subcommands:
                index += 1
                child = command.subcommands.get(name)
                assert child is not None
                command = child
            else:
                break

        rest: list[str] = names[index:]

        return command, rest

    def complete(
        self, param_name: str
    ) -> t.Callable[[at.CompletionFunc], at.CompletionFunc]:
        param = self.get_param(param_name)
        if param:

            def inner(func: at.CompletionFunc) -> at.CompletionFunc:
                param.comp_func = func  # type: ignore
                return func

            return inner

        raise errors.ParamError(
            f"No parameter with name: {param_name}",
            Join.with_space(self.doc.fullname),
        )

    def get(self, param_name: str) -> t.Callable[[at.ParamGetter], at.ParamGetter]:
        param = self.get_param(param_name)
        if param:

            def inner(func: at.ParamGetter) -> at.ParamGetter:
                param.getter_func = func  # type: ignore
                return func

            return inner

        raise errors.ParamError(
            f"No parameter with name: {param_name}",
            Join.with_space(self.doc.fullname),
        )

    @staticmethod
    def wrap_class_callback(cls: type[at.ClassCallback]) -> at.CommandCallback:
        if not hasattr(cls, "handle"):
            raise errors.CommandError("class-style commands require a handle() method")

        def wrapper(**kwargs: t.Any) -> t.Any:
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
    name: str | None = None,
    /,
    *,
    desc: str | None = None,
    config: Config | None = None,
    **kwargs: t.Any,
) -> t.Callable[[at.CommandCallback], Command]:
    ...


def command(
    first: at.CommandCallback | str | None = None,
    /,
    *,
    desc: str | None = None,
    config: Config | None = None,
    **kwargs: t.Any,
) -> t.Callable[[at.CommandCallback], Command] | Command:
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
        config (Config | None, optional): Configuration object to apply
            to this command. If one is not provided, the default is used
    """

    name = None

    def inner(callback: at.CommandCallback) -> Command:
        cmdconfig = config or Config.load()
        command_name = Command.get_canonical_subcommand_name(
            callback, name, cmdconfig.transform_snake_case
        )

        command = Command(
            callback=callback,
            config=cmdconfig,
            name=command_name,
            description=desc,
            parent=None,
            explicit_name=bool(name),
            autoload=True,
            **kwargs,
        )
        command.use(ExecMiddleware.all())
        return command

    if isinstance(first, str) or first is None:
        name = first
        return inner
    else:
        return inner(first)


def namespace(
    name: str,
    *,
    desc: str | None = None,
    config: Config | None = None,
    **kwargs: t.Any,
) -> Command:
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
    config = config or Config.load()

    command = Command(
        callback=namespace_callback,
        config=config,
        name=name,
        description=desc,
        parent=None,
        autoload=True,
        **kwargs,
    )
    command.use(ExecMiddleware.all())
    return command


def namespace_callback(ctx: Context) -> t.NoReturn:
    command = ctx.command
    arc.usage(command)
    help_call = color.colorize(
        f"{command.root.name} {Join.with_space(command.doc.fullname)} --help",
        color.fg.YELLOW,
    )
    arc.info(f"{help_call} for more information")
    arc.exit(1)
