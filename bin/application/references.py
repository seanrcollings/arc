from pathlib import Path
import shutil
import sys

import arc

from .constants import SRC_DIR, DOCS_DIR


REFERENCE_DIR = DOCS_DIR / "docs" / "reference"
EXCLUDE = ["api", "constants", "suggest"]


def init():
    if REFERENCE_DIR.is_dir():
        shutil.rmtree(REFERENCE_DIR)

    REFERENCE_DIR.mkdir()


def generate_reference():
    init()

    for path in SRC_DIR.glob("**/*.py"):
        if path.name.startswith("_"):
            continue

        module = ".".join([*path.parts[1:-1], path.stem])
        if module in EXCLUDE:
            continue

        ref_path = REFERENCE_DIR / Path(*path.parts[1:-1], f"{path.stem}.md")
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        arc.log(module, "->", ref_path, file=sys.stderr)
        with ref_path.open("w") as f:
            f.write(f"# {module}\n")
            f.write(f"::: arc.{module}")
