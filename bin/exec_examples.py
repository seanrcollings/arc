import logging
import typing as t
import sys
from pathlib import Path
import shlex
import shutil
import contextlib
from dataclasses import dataclass

import yaml
from arc.config import config as ac

ROOT_DIR = Path(".")
DOCS_DIR = ROOT_DIR / "docs"
EXAMPLE_DIR = DOCS_DIR / "examples"
OUTPUT_DIR = EXAMPLE_DIR / "outputs"


@dataclass
class ExecConfig:
    file: str
    """The file to attempt to load"""
    out: Path
    """The name of the output file"""
    name: str
    """The name of the executable"""
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


def get_config(file):
    config: list[ExecConfig] = []
    with open(file, "r") as file:
        for item in yaml.load(file.read(), yaml.CLoader):
            if not item.get("name", None):
                item["name"] = item["file"]

            if item.get("out", None):
                item["out"] = Path(item["out"])
            else:
                item["out"] = Path(item["file"].rstrip(".py"))

            if isinstance(item.get("exec", None), str):
                item["exec"] = [item["exec"]]

            config.append(ExecConfig(**item))

    return config


def exec_examples(config: list[ExecConfig]):
    for entry in config:
        ac.version = None

        with open(EXAMPLE_DIR / entry.file) as f:
            contents = f.read()

        (OUTPUT_DIR / entry.out).parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_DIR / entry.out, "w+") as f:
            print(entry.file, "->", entry.out)
            stderr = sys.stderr
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                for args in entry.exec:
                    logging.root.handlers.clear()
                    f.write(f"$ python {entry.name} {args}\n")
                    sys.argv = [entry.name, *shlex.split(args)]

                    try:
                        exec(contents, {})
                    except SystemExit as e:
                        if e.code != entry.exit_code:
                            stderr.write(
                                f"{entry.file} exited with {str(e)} exit code\n"
                            )
                            raise
                    except Exception as e:
                        if not entry.error_allowed:
                            stderr.write(str(e))
                            raise

    print("\nFinished!")


def main():
    print("--- EXECUTING EXAMPLES ---")
    init()
    config = get_config(DOCS_DIR / "examples.yaml")
    exec_examples(config)


main()
