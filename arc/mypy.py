# pylint: disable=no-name-in-module
from mypy.mro import calculate_mro
from mypy.plugin import Plugin, DynamicClassDefContext
from mypy.types import UnboundType
from mypy.nodes import (
    TypeInfo,
    SymbolTable,
    ClassDef,
    Block,
    SymbolTableNode,
    GDEF,
)


STRICT_FUNCTIONS = {
    "arc.types.network.stricturl",
    "arc.types.path.strictpath",
    "arc.types.numbers.strictint",
    "arc.types.numbers.strictfloat",
    "arc.types.strings.strictstr",
}


class ArcPlugin(Plugin):
    def get_dynamic_class_hook(self, fullname: str):
        if fullname in STRICT_FUNCTIONS:
            return dynamic_class_hook
        return None


# https://github.com/dropbox/sqlalchemy-stubs/blob/81e44ae30f6d13d29be4abbcb76a9d03880bc165/sqlmypy.py#L173
def dynamic_class_hook(ctx: DynamicClassDefContext):
    class_def = ClassDef(ctx.name, Block([]))
    class_def.fullname = ctx.api.qualified_name(ctx.name)

    info = TypeInfo(SymbolTable(), class_def, ctx.api.cur_mod_id)
    class_def.info = info
    node = ctx.call.callee.node  # type: ignore

    if isinstance(node.type.ret_type, UnboundType):
        ctx.api.analyze_func_def(node)  # type: ignore

    info.bases = [node.type.ret_type.item]
    calculate_mro(info)

    ctx.api.add_symbol_table_node(ctx.name, SymbolTableNode(GDEF, info))


def plugin(_version: str):
    return ArcPlugin
