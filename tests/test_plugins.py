from pathlib import Path
import pytest

import arc


class TestPathPlugins:
    @pytest.fixture(scope="function")
    def plugin_path(self, tmp_path_factory: pytest.TempPathFactory):
        path = tmp_path_factory.mktemp("data") / "test_plugin.py"
        with path.open("w") as f:
            f.write(
                """
import arc

def plugin(ctx):
    command = ctx.root

    @command.subcommand
    def test():
        return 2

    """
            )
        return path

    def test_load(self, plugin_path: Path):
        @arc.command
        def command():
            ...

        app = arc.App(command)
        app.plugins.paths(str(plugin_path))
        assert str(plugin_path) in app.plugins

    def test_load_dir(self, plugin_path: Path):
        @arc.command
        def command():
            ...

        app = arc.App(command)
        app.plugins.paths(str(plugin_path.parent))
        assert str(plugin_path) in app.plugins


# TODO: Test entrypoint plugins (not sure how to do this)
