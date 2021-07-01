import os
import enum
import webbrowser
import subprocess
import re
from pathlib import Path

import pdoc  # type: ignore
from arc import CLI, ParsingMethod, color

cli = CLI("arc")


class OpenEnum(enum.Enum):
    SOURCE = "source"
    WIKI = "wiki"
    DOCS = "docs"


open_map = {
    OpenEnum.SOURCE: "https://github.com/seanrcollings/arc",
    OpenEnum.WIKI: "https://github.com/seanrcollings/arc/wiki",
    OpenEnum.DOCS: "http://arc.seanrcollings.com/arc.html",
}


@cli.command(("open", "o"), parsing_method=ParsingMethod.POSITIONAL)
def open_link(name: OpenEnum):
    """Opens an arc related link"""
    webbrowser.open(open_map[name])


if os.getenv("ARC_DEVELOPMENT") == "true":

    def color_print(message: str):
        print(f"{color.fg.ARC_BLUE}{message}{color.effects.CLEAR}")

    @cli.command(("deploy", "d"), parsing_method=ParsingMethod.POSITIONAL)
    def deploy(version: str):
        """Handle the details of deploying a new version of arc"""
        root = (Path(__file__) / "../../../").resolve()
        color_print("Running Tests...")
        subprocess.run(["pytest", root / "tests"], check=True)
        color_print("Updating pyproject.toml version...")
        subprocess.run(["poetry", "version", version], check=True)

        color_print("Updating __version__...")
        init = root / "arc" / "__init__.py"
        with init.open("r+") as f:
            subbed = re.sub(
                r"__version__ = .+\n",
                f'__version__ = "{version}"',
                f.read(),
            )
            f.seek(0)
            f.write(subbed)

        color_print("Updating API Docs...")
        pdoc.render.configure(docformat="google")
        pdoc.pdoc(root / "arc", output_directory=root / "docs")

        color_print("Commiting Changes...")
        subprocess.run(("git", "add", "."), check=True)
        subprocess.run(("git", "commit", "-m", f"Version {version}"), check=True)
        subprocess.run(("git", "tag", f"v{version}"), check=True)

        color_print("Publishing...")
        subprocess.run(("poetry", "publish", "--build"), check=True)
