import sys

from arc.parser.data_types import ScriptNode
from .script import Script


class RawScript(Script):
    def execute(self, script_node):
        if self.meta:
            self.function(*sys.argv, meta=self.meta)
        else:
            self.function(*sys.argv)

    def match_input(self, script_node: ScriptNode):
        pass
