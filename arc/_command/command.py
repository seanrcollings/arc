from __future__ import annotations
import contextlib
import re
from functools import cached_property
import typing as t
import shlex
import sys

from arc import errors, logging, utils
from arc.color import colorize, effects, fg
from arc._command.param_builder import ParamBuilder, wrap_class_callback
from arc.context import Context
from arc.parser import Parser
from arc.present.help_formatter import HelpFormatter
from arc.config import config
from arc.typing import ClassCallback
from arc import callback as acb
from .param_mixin import ParamMixin


logger = logging.getArcLogger("command")
DEFAULT_SECTION: str = config.default_section_name


class Command(ParamMixin):
    builder = ParamBuilder
    parser = Parser

    def __init__(
        self,
        callback: t.Callable,
        name: str = "",
        state: t.Optional[dict] = None,
        description: t.Optional[str] = None,
        **ctx_dict,
    ):
        self._callback = callback
        self.name = name
        self.subcommands: dict[str, Command] = {}
        self.subcommand_aliases: dict[str, str] = {}
        self.state = state or {}
        self._description = description
        self.ctx_dict = ctx_dict
        self.callbacks: set[acb.Callback] = set()

        if config.environment == "development":
            # Constructs the params at instantiation.
            # if there's something wrong with a param,
            # this will raise an error. If we don't do this,
            # the error woudln't be raised until executing
            # the command, so it could easy to miss
            self.params

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

    def schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "doc": self._callback.__doc__,
            "context": self.state,
            "subcommands": {
                name: command.schema() for name, command in self.subcommands.items()
            },
            "parameters": {name: param.schema() for name, param in self.params.items()},
        }

    # Command Execution ------------------------------------------------------------
    def __call__(self, *args, **kwargs):
        with contextlib.redirect_stdout(utils.IoWrapper(sys.stdout)):
            return self.main(*args, **kwargs)

    @utils.timer("Running Command")
    def main(
        self,
        args: t.Union[str, list[str]] = None,
        fullname: str = None,
        **kwargs,
    ):
        ctx_dict = self.ctx_dict | kwargs

        if not self.name:
            self.name = utils.discover_name()

        with self.create_ctx(fullname or self.name, **ctx_dict) as ctx:
            try:
                try:
                    args = t.cast(list[str], self.get_args(args))

                    self.parse_args(ctx, args)
                    return self.execute(ctx)
                except errors.ArcError as e:
                    if config.environment == "development":
                        raise

                    print(str(e))
                    raise errors.Exit(1)

            except errors.Exit as e:
                if config.environment == "development" and e.code != 0:
                    raise
                sys.exit(e.code)

    def execute(self, ctx: Context):
        utils.header("EXECUTION")
        if not self._callback:
            raise RuntimeError("No callback associated with this command to execute")

        return ctx.execute(self._callback, **ctx.args)

    def get_args(self, args: t.Union[str, list[str]] = None) -> list[str]:
        if isinstance(args, str):
            args = shlex.split(args)
        elif args is None:
            args = sys.argv[1:]

        return args

    def create_ctx(self, fullname: str, **kwargs):
        ctx = Context(self, fullname=fullname, **kwargs)
        return ctx

    def create_parser(self, ctx: Context, **kwargs):
        parser = self.parser(ctx, **kwargs)
        for param in self.visible_params:
            parser.add_param(param)

        return parser

    def parse_args(self, ctx: Context, args: list[str], **kwargs):
        parser = self.create_parser(ctx, **kwargs)
        parsed, extra = parser.parse(args)

        ctx.extra = extra

        for param in self.params:
            value = param.process_parse_result(ctx, parsed)
            if param.expose:
                ctx.args[param.arg_name] = value

    # Subcommand Construction ------------------------------------------------------------

    def subcommand(
        self,
        name: t.Union[str, list[str], tuple[str, ...]] = None,
        description: t.Optional[str] = None,
        state: dict[str, t.Any] = None,
    ):
        """Decorator used to tranform a function into a subcommand of `self`

        Args:
            name (Union[str, list[str], tuple[str, ...]], optional): The name to reference
                this subcommand by. Can optionally be a `list` of names. In this case,
                the first in the list will be treated as the "true" name, and the others
                will be treated as aliases. If no value is provided, `function.__name__` is used

            description (Optional[str]): Description of the command's function. Will be used
                 in the `--help` documentation

            state (dict[str, Any], optional): Special data that will be
                passed to this command (and any subcommands) at runtime. Defaults to None.

        Returns:
            Command: the subcommand created
        """

        def decorator(callback: t.Union[t.Callable, Command, type[ClassCallback]]):
            # Should we allow this?
            if isinstance(callback, Command):
                callback = callback._callback

            if isinstance(callback, type):
                if isinstance(callback, ClassCallback):
                    # inspect.signature() can potentially be a heavy operation.
                    # wrapping the callback here, means that we would call it for
                    # every class command.
                    # TODO: Make this lazy like function commands
                    callback = wrap_class_callback(callback)  # type: ignore
                else:
                    raise errors.CommandError(
                        f"Command classes must have a {colorize('handle()', fg.YELLOW)} method"
                    )

            callback_name = callback.__name__
            if config.transform_snake_case:
                callback_name = callback_name.replace("_", "-")

            command_name = self.handle_command_aliases(name or callback_name)
            command = Command(callback, command_name, state, description)
            return self.install_command(command)

        return decorator

    def install_commands(self, *commands):
        return tuple(self.install_command(command) for command in commands)

    def install_command(self, command: "Command"):
        """Installs a command object as a subcommand
        of the current object"""
        # Commands created with @command do not have a name by default
        # to faccilitate automatic name discovery. When they are added
        # to a parent command, a name needs to be added
        if not command.name:
            command.name = command._callback.__name__

        self.subcommands[command.name] = command
        command.callbacks = self.inheritable_callbacks()

        logger.debug(
            "Registered %s%s%s command to %s%s%s",
            fg.YELLOW,
            command.name,
            effects.CLEAR,
            fg.YELLOW,
            self.name,
            effects.CLEAR,
        )

        return command

    # Helpers ------------------------------------------------------------

    def handle_command_aliases(
        self, command_name: t.Union[str, list[str], tuple[str, ...]]
    ) -> str:
        if isinstance(command_name, str):
            return command_name

        name = command_name[0]
        aliases = command_name[1:]

        for alias in aliases:
            self.subcommand_aliases[alias] = name

        return name

    def is_namespace(self):
        from .. import command_builders

        return self._callback is command_builders.helper

    ## Documentation Helpers ---------------------------------------------------------

    def get_help(self, ctx: Context) -> str:
        formatter = HelpFormatter()
        formatter.write_help(self, ctx)
        return formatter.value

    def get_usage(self, ctx: Context, help_hint: bool = True) -> str:
        formatter = HelpFormatter()
        formatter.write_usage(self, ctx)
        if help_hint:
            formatter.write_paragraph()
            formatter.write_text(
                f"Try {colorize(ctx.fullname + ' ' + '--help', fg.ARC_BLUE)} for more information"
            )
        return formatter.value

    @cached_property
    def parsed_docstring(self):
        """Parsed docstring for the command

        Sections are denoted by a new line, and
        then a line beginning with `#`. Whatever
        comes after the `#` will be the key in
        the sections dict. And all content between
        that `#` and the next `#` will be the value.

        The first section of the docstring is not
        required to possess a section header, and
        will be entered in as the `description` section.
        """
        parsed: dict[str, str] = {DEFAULT_SECTION: ""}
        if not self.doc:
            return {}

        lines = [line.strip() for line in self.doc.split("\n")]

        current_section = DEFAULT_SECTION

        for line in lines:
            if line.startswith("#"):
                current_section = line[1:].strip().lower()
                parsed[current_section] = ""
            else:
                parsed[current_section] += line + "\n"

        return parsed

    @property
    def doc(self):
        return self._callback.__doc__

    @property
    def description(self) -> t.Optional[str]:
        return self._description or self.parsed_docstring.get("description")

    @property
    def short_description(self) -> t.Optional[str]:
        description = self.description
        return description if description is None else description.split("\n")[0]

    @cached_property
    def _parsed_argument_section(self) -> t.Optional[dict[str, str]]:
        arguments = self.parsed_docstring.get("arguments")
        if not arguments:
            return None

        parsed: dict[str, str] = {}
        regex = re.compile(r"^\w+:.+")
        current_param = ""

        for line in arguments.splitlines():
            if regex.match(line):
                param, first_line = line.split(":", maxsplit=1)
                current_param = param
                parsed[current_param] = first_line.strip()
            elif current_param:
                parsed[current_param] += " " + line.strip()

        return parsed

    def update_param_descriptions(self):
        """Parses the function docstring, then updates
        parameters with the associated description in the arguments section
        if the param does not have a description already.
        """
        descriptions = self._parsed_argument_section
        if not descriptions:
            return

        for param in self.params:
            if not param.description:
                param.description = descriptions.get(param.arg_name)

    # Callbacks ------------------------------------------------------
    def callback(
        self, callback: acb.CallbackFunc = None, *, inherit: bool = True
    ) -> t.Callable[[acb.CallbackFunc], acb.Callback]:
        def inner(callback: acb.CallbackFunc) -> acb.Callback:
            cb = acb.create(inherit=inherit)(callback)
            self.callbacks.add(cb)
            return cb

        if callback:
            return inner(callback)  # type: ignore

        return inner

    def inheritable_callbacks(self):
        return {callback for callback in self.callbacks if callback.inherit}
