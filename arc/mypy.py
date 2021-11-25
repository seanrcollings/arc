from arc.types import Url
from mypy.plugin import Plugin, DynamicClassDefContext  # type: ignore
from mypy.nodes import TypeInfo, SymbolTable, ClassDef, Block

STRICT_FUNCTIONS = {"arc.types.network.stricturl"}


class ArcPlugin(Plugin):
    def get_dynamic_class_hook(self, fullname: str):
        print(fullname)
        if fullname in STRICT_FUNCTIONS:
            return self.__create_type_info

    def __create_type_info(self, ctx: DynamicClassDefContext):
        table = SymbolTable()
        defn = ClassDef(ctx.name, Block([]))
        info = TypeInfo(table, defn, "manage")
        ctx.api.add_symbol_table_node(ctx.name, info, ctx)


def plugin(version: str):
    return ArcPlugin
