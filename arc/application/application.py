import os
import enum
import webbrowser
import subprocess
import re
from pathlib import Path

from arc import CLI, ParsingMethod, color, __version__

from .templates import templates

cli = CLI("arc", version=__version__)

#####  OPEN  #####
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


#####  INIT  #####
class InitEnum(enum.Enum):
    POETRY = "poetry"


def classify(string: str):
    return "".join(word.title() for word in string.split("_"))


@cli.command(("init", "i"), parsing_method=ParsingMethod.POSITIONAL)
def init_command(name: str, method: InitEnum):
    """Initalize a new arc-based Python project"""
    project = Path(os.getcwd() + f"/{name}")
    if method == InitEnum.POETRY:
        subprocess.run(("poetry", "new", name), check=True)
        subprocess.run(("poetry", "add", "arc-cli"), cwd=project, check=True)
        name = name.replace("-", "_")
        with open(project / "pyproject.toml", "a") as f:
            f.write(f'\n[tool.poetry.scripts]\n{name} = "{name}.cli:cli"')

        subprocess.run(("poetry", "install"), cwd=project, check=True)

        target_dir = project / name

    for file_name, template in templates.items():
        with open(target_dir / f"{file_name}.py", "w+") as f:
            f.write(template.format(name=name, class_name=classify(name)))


####  DEPLOY  ####
if os.getenv("ARC_DEVELOPMENT") == "true":
    import pdoc  # type: ignore
    import pdoc.web  # type: ignore

    root = (Path(__file__) / "../../../").resolve()

    def color_print(message: str):
        print(f"{color.fg.ARC_BLUE}{message}{color.effects.CLEAR}")

    @cli.command(("deploy", "d"), parsing_method=ParsingMethod.POSITIONAL)
    def deploy(version: str):
        """Handle the details of deploying a new version of arc"""
        color_print("Running Tests...")
        subprocess.run(["pytest", root / "tests"], check=True)
        color_print("Updating pyproject.toml version...")
        subprocess.run(["poetry", "version", version], check=True)

        color_print("Updating __version__...")
        init = root / "arc" / "__init__.py"
        with init.open("r+") as f:
            subbed = re.sub(
                r"__version__ = \".+\"\n",
                f'__version__ = "{version}    "',
                f.read(),
            )
            f.seek(0)
            f.write(subbed)

        color_print("Updating API Docs...")
        compile_docs()

        color_print("Update changelog")
        subprocess.run(
            (os.getenv("EDITOR", "nano"), root / "wiki/Changelog.md"), check=True
        )

        color_print("Commiting Changes...")
        subprocess.run(("git", "add", "."), check=True)
        subprocess.run(("git", "commit", "-m", f"Version {version}"), check=True)
        subprocess.run(("git", "tag", f"v{version}"), check=True)

        color_print("Publishing...")
        subprocess.run(("poetry", "publish", "--build"), check=True)

        color_print("Deployed!")

    @cli.command()
    def docs():
        """Starts a http server to serve development pdocs"""
        host = "localhost"
        port = 8080
        all_modules = pdoc.extract.walk_specs((root / "arc",))
        pdoc.render.configure(docformat="google")
        with pdoc.web.DocServer((host, port), all_modules) as httpd:
            url = f"http://{host}:{port}"
            print(f"pdoc server ready at {url}")
            webbrowser.open(url)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.server_close()

    @docs.subcommand("compile")
    def compile_docs():
        """Compiles the documentation"""
        pdoc.render.configure(docformat="google")
        pdoc.pdoc(root / "arc", output_directory=root / "docs")
