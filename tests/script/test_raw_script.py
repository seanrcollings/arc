import sys
from unittest.mock import patch
from tests.script.base_script_test import BaseScriptTest
from arc.script import RawScript


class TestRawScript(BaseScriptTest):
    script_class = RawScript

    def test_raw_script(self):
        script = self.create_script(lambda *args: args)
        args = ["exec", "test=2", "test=4"]
        with patch.object(sys, "argv", args):
            script(self.create_script_node())
            script.function.assert_called_with(*args)

    # Overide these because the RawScript doesn't check ANYTHING
    def test_nonexistant_options(self):
        pass

    def test_nonexistant_flag(self):
        pass

    def test_meta(self):
        script = self.create_script(
            lambda *args, meta: meta, annotations={"a": int}, meta={"val": 2}
        )
        args = ["exec", "test=2", "test=4"]
        with patch.object(sys, "argv", args):
            script(self.create_script_node())

        script.function.assert_called_with(*args, meta={"val": 2})
