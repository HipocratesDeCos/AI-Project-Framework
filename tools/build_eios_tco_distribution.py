"""Build optional procurement TCO wheel exclusively from existing canonical code.

The current TCOInput still owns PurchaseOperation from eios.core.models, now
supplied ONLY by the shared eios-contracts-procurement distribution. It is
procurement-specific, not a general-purpose business engine.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
METADATA_FILE = Path("packaging/eios-tco-procurement/pyproject.toml")
SOURCE_FILES = (
    Path("eios/tco/__init__.py"),
    Path("eios/tco/models.py"),
    Path("eios/tco/engine.py"),
)
DISTRIBUTION = "eios-tco-procurement"
PACKAGE_VERSION = "0.2.0"

ALLOWED_INTERNAL_IMPORTS = frozenset({
    "eios.core.models",
    "eios.tco.models",
    "eios.tco.engine",
})


def verify_source_dependencies(root: Path = ROOT) -> None:
    """Reject any new internal dependency outside the audited file allowlist."""
    for path in SOURCE_FILES:
        module = path.parent.as_posix().replace("/", ".")
        source = root / path
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = (alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 1:
                    raise ValueError(f"Forbidden relative import: {path}")
                if node.level == 1:
                    if not node.module:
                        raise ValueError(f"Relative import must name a module: {path}")
                    modules = (f"{module}.{node.module}",)
                else:
                    modules = (node.module or "",)
            else:
                continue
            for dependency in modules:
                if (dependency == "eios" or dependency.startswith("eios.")) and (
                    dependency not in ALLOWED_INTERNAL_IMPORTS
                ):
                    raise ValueError(
                        f"Forbidden unbundled EIOS dependency in {path}: {dependency}"
                    )


def stage_distribution(destination: Path, root: Path = ROOT) -> None:
    verify_source_dependencies(root)
    source = destination / "src"
    source.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / METADATA_FILE, destination / "pyproject.toml")
    for path in SOURCE_FILES:
        target = source / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / path, target)


def audit_wheel(wheel: Path) -> None:
    """Validate the real wheel payload, not merely pyproject configuration."""
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        pyfiles = {name for name in names if name.endswith(".py")}
        expected = {path.as_posix() for path in SOURCE_FILES}
        if pyfiles != expected:
            raise ValueError(f"Unexpected TCO wheel modules: {sorted(pyfiles ^ expected)}")
        if any(name.startswith("eios/") and name not in expected for name in names):
            raise ValueError("TCO wheel contains files beyond its canonical module allowlist")
        if any(".data/" in name for name in names):
            raise ValueError("TCO wheel contains unapproved payload data")
        metadata_files = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_files) != 1:
            raise ValueError("TCO wheel requires one METADATA record")
        lines = archive.read(metadata_files[0]).decode("utf-8").splitlines()
        if "Name: eios-tco-procurement" not in lines:
            raise ValueError("Invalid TCO distribution identity")
        if "Version: 0.2.0" not in lines:
            raise ValueError("Invalid TCO distribution version")
        deps = [line for line in lines if line.startswith("Requires-Dist:")]
        names = [item.split(":", 1)[1].strip().split(" ", 1)[0].split("=", 1)[0].split("<", 1)[0].lower() for item in deps]
        if sorted(names) != ["eios-contracts-procurement", "pydantic"]:
            raise ValueError("TCO wheel must depend on Pydantic and shared C0 contracts only")
        if not any("eios-contracts-procurement==0.1.0" in item.replace(" ", "") for item in deps):
            raise ValueError("TCO wheel must pin exact shared C0 contract version")


def build(output: Path, root: Path = ROOT) -> Path:
    with tempfile.TemporaryDirectory(prefix="eios-tco-build-") as workspace:
        base = Path(workspace)
        staged = base / "source"
        wheels = base / "wheels"
        stage_distribution(staged, root)
        wheels.mkdir()
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps",
             "--no-build-isolation", "--wheel-dir", str(wheels), str(staged)],
            check=True,
        )
        candidates = list(wheels.glob("eios_tco_procurement-*.whl"))
        if len(candidates) != 1:
            raise ValueError("Expected exactly one optional TCO wheel")
        audit_wheel(candidates[0])
        output.mkdir(parents=True, exist_ok=True)
        destination = output / candidates[0].name
        shutil.copy2(candidates[0], destination)
        return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/tco"))
    args = parser.parse_args()
    wheel = build(args.output.resolve())
    print(f"Audited optional TCO wheel: {wheel}")


if __name__ == "__main__":
    main()
