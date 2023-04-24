from pathlib import Path
import shutil

ROOT_DIR = Path(".")
SRC_DIR = ROOT_DIR / "arc"
DOCS_DIR = ROOT_DIR / "docs"
REFERENCE_DIR = DOCS_DIR / "docs" / "reference"
EXCLUDE = ["api", "constants", "suggest"]


def init():
    if REFERENCE_DIR.is_dir():
        shutil.rmtree(REFERENCE_DIR)

    REFERENCE_DIR.mkdir()


def main():
    print("--- GENERATING REFERENCE DOCS ---")
    init()

    for path in SRC_DIR.glob("**/*.py"):
        if path.name.startswith("_"):
            continue

        module = ".".join([*path.parts[1:-1], path.stem])
        if module in EXCLUDE:
            continue

        ref_path = REFERENCE_DIR / Path(*path.parts[1:-1], f"{path.stem}.md")
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        print(module, "->", ref_path)
        with ref_path.open("w") as f:
            f.write(f"# {module}\n")
            f.write(f"::: arc.{module}")


if __name__ == "__main__":
    main()
