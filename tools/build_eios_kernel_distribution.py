"""Build the independent EIOS kernel wheel from the ONE canonical source tree.

The legacy eios-mvp distribution is untouched. This script stages only approved
neutral files, builds a standard PEP 517 wheel and inspects its actual contents.
Requires setuptools and wheel in the build environment (CI installs both).
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
METADATA_FILE = Path("packaging/eios-kernel/pyproject.toml")
SOURCE_FILES = (
    Path("eios/kernel/execution.py"),
    Path("eios/parameters/center.py"),
)
PACKAGE_NAME = "eios-kernel"


def verify_source_dependencies(root: Path = ROOT) -> None:
    """Reject internal EIOS imports, even if a future source edit adds one."""
    for relative in SOURCE_FILES:
        source = root / relative
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    raise ValueError(f"Relative dependency forbidden in kernel: {relative}")
                names = [node.module or ""]
            else:
                continue
            if any(name == "eios" or name.startswith("eios.") for name in names):
                raise ValueError(f"Internal EIOS dependency forbidden in kernel: {relative}")


def stage_distribution(destination: Path, root: Path = ROOT) -> None:
    """Create an isolated PEP 517 project; do not duplicate canonical source."""
    verify_source_dependencies(root)
    target = destination / "src"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / METADATA_FILE, destination / "pyproject.toml")
    for relative in SOURCE_FILES:
        output = target / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / relative, output)


def audit_wheel(wheel: Path) -> None:
    """Accept only the two neutral modules and the intended base dependency."""
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        actual = {name for name in names if name.endswith(".py")}
        expected = {str(path).replace("\\", "/") for path in SOURCE_FILES}
        if actual != expected:
            raise ValueError(f"Unexpected Python modules: {sorted(actual ^ expected)}")
        meta = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(meta) != 1:
            raise ValueError("Expected exactly one wheel METADATA record")
        metadata = archive.read(meta[0]).decode("utf-8")
        fields = metadata.splitlines()
        if "Name: eios-kernel" not in fields:
            raise ValueError("Wrong package identity")
        dependencies = [line for line in fields if line.startswith("Requires-Dist:")]
        if not dependencies or any("pydantic" not in line.lower() for line in dependencies):
            raise ValueError("Only the required Pydantic runtime dependency is permitted")
        if len(dependencies) != 1:
            raise ValueError("Unexpected additional runtime dependency")


def build(output: Path, root: Path = ROOT) -> Path:
    with tempfile.TemporaryDirectory(prefix="eios-kernel-build-") as temp_dir:
        temp = Path(temp_dir)
        staging = temp / "staging"
        wheels = temp / "wheels"
        stage_distribution(staging, root)
        wheels.mkdir()
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps",
             "--no-build-isolation", "--wheel-dir", str(wheels), str(staging)],
            check=True,
        )
        candidates = list(wheels.glob("eios_kernel-*.whl"))
        if len(candidates) != 1:
            raise ValueError("Expected exactly one EIOS kernel wheel")
        audit_wheel(candidates[0])
        output.mkdir(parents=True, exist_ok=True)
        final = output / candidates[0].name
        if final.exists():
            final.unlink()
        shutil.copy2(candidates[0], final)
        return final


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/kernel"))
    args = parser.parse_args()
    wheel = build(args.output.resolve())
    print(f"Audited independent kernel wheel: {wheel}")


if __name__ == "__main__":
    main()
