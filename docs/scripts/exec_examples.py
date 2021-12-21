import sys
from pathlib import Path
import importlib
import shlex
import shutil
import contextlib
import io
from dataclasses import dataclass

import yaml
from arc import errors, utils


PARENT = Path(__file__).parent
EXAMPLE_DIR = PARENT.parent / "examples"
OUTPUT_DIR = EXAMPLE_DIR / "outputs"


@dataclass
class ExecConfig:
    file: str
    """The file to attempt to load"""
    out: str
    """The name of the output file"""
    exit_code: int = 0
    """The expected exit code (if SystemExit is raised)"""
    error_allowed: bool = False
    """Stops errors from termintation execution"""
    exec: str = ""
    """String to execute the file with. Placed into `argv`"""


def init():
    if OUTPUT_DIR.is_dir():
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir()


def exec_examples(config: list[ExecConfig]):

    sys.path.append(str(EXAMPLE_DIR))
    for entry in config:
        with contextlib.redirect_stdout(io.StringIO()) as f:
            path = EXAMPLE_DIR / entry.file
            sys.path.append(str(path.parent))

            args = [entry.file]
            if entry.exec:
                args.extend(shlex.split(entry.exec))

            sys.argv = args
            try:
                importlib.import_module(path.stem)
            except SystemExit as e:
                if e.code != entry.exit_code:
                    raise
            except Exception:
                if not entry.error_allowed:
                    raise

            sys.path.pop()

        output = f"$ python {entry.file} {entry.exec}\n" + utils.ansi_clean(
            f.getvalue()
        )
        outfile = OUTPUT_DIR / entry.out
        outfile.touch()
        outfile.write_text(output)


def main():
    init()

    with open(PARENT / "exec.yaml", "r") as file:
        config: list[ExecConfig] = [
            ExecConfig(**item) for item in yaml.load(file.read(), yaml.CLoader)
        ]

    exec_examples(config)


main()