import typing as t
import sys
from pathlib import Path
import importlib
import shlex
import shutil
import contextlib
import io
from dataclasses import dataclass

from arc import errors, utils
import yaml


PARENT = Path(__file__).parent
EXAMPLE_DIR = PARENT.parent / "examples"
OUTPUT_DIR = EXAMPLE_DIR / "outputs"


@dataclass
class ExecConfig:
    file: str
    """The file to attempt to load"""
    out: t.Optional[str] = None
    """The name of the output file"""
    exit_code: int = 0
    """The expected exit code (if SystemExit is raised)"""
    error_allowed: bool = False
    """Stops errors from termintation execution"""
    exec: t.Union[list[str], str] = ""
    """String to execute the file with. Placed into `argv`"""


def init():
    if OUTPUT_DIR.is_dir():
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir()


def exec_examples(config: list[ExecConfig]):

    sys.path.append(str(EXAMPLE_DIR))
    module = None
    for entry in config:
        path = EXAMPLE_DIR / entry.file
        sys.path.append(str(path.parent))

        execs = entry.exec
        if isinstance(execs, str):
            execs = [execs]
        try:
            with contextlib.redirect_stdout(io.StringIO()) as f:
                for execute in execs:

                    f.write(f"$ python {entry.file} {execute}\n")

                    args = [entry.file]
                    if execute:
                        args.extend(shlex.split(execute))

                    sys.argv = args

                    if module:
                        module = importlib.reload(module)
                    else:
                        module = importlib.import_module(path.stem)

                    f.write("\n")

        except SystemExit as e:
            if e.code != entry.exit_code:
                print(f.getvalue())
                raise
        except Exception:
            if not entry.error_allowed:
                raise

        module = None

        sys.path.pop()
        output = utils.ansi_clean(f.getvalue())
        outfile = OUTPUT_DIR / (entry.out or path.stem)
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