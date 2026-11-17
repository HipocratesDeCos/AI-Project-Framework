"""F5.6 — auditable optional neutral input-contracts wheel from canonical source."""
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
METADATA_FILE = Path("packaging/eios-input-contracts/pyproject.toml")
SOURCE_FILES = (
    Path("eios/input_contracts/__init__.py"),
    Path("eios/input_contracts/contracts.py"),
)
ALLOWED_IMPORTS = frozenset({
    "eios.input_contracts.contracts", "eios.kernel.execution",
})


def verify_source_dependencies(root: Path = ROOT) -> None:
    """Allow only the neutral kernel, never EIOS business/domain imports."""
    for rel in SOURCE_FILES:
        source = root / rel
        module_package = ".".join(rel.parts[:-1])
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(rel))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports = (alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 1:
                    raise ValueError(f"Forbidden relative import: {rel}")
                if node.level == 1:
                    if not node.module:
                        raise ValueError(f"Explicit module required for relative import: {rel}")
                    imports = (f"{module_package}.{node.module}",)
                else:
                    imports = (node.module or "",)
            else:
                continue
            for name in imports:
                if (name == "eios" or name.startswith("eios.")) and name not in ALLOWED_IMPORTS:
                    raise ValueError(f"Forbidden EIOS business dependency: {rel}: {name}")


def stage_distribution(destination: Path, root: Path = ROOT) -> None:
    verify_source_dependencies(root)
    stage = destination / "src"
    stage.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / METADATA_FILE, destination / "pyproject.toml")
    for rel in SOURCE_FILES:
        target = stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, target)


def audit_wheel(wheel: Path) -> None:
    """Inspect installed filenames, exact metadata and imports in the wheel bytes."""
    with zipfile.ZipFile(wheel) as archive:
        listed = archive.namelist()
        names = set(listed)
        if len(names) != len(listed):
            raise ValueError("Duplicate input-contract ZIP paths")
        expected = {path.as_posix() for path in SOURCE_FILES}
        if {item for item in names if item.endswith(".py")} != expected:
            raise ValueError("Unexpected input-contract Python modules")
        if any(item.startswith("eios/") and item not in expected for item in names):
            raise ValueError("Input-contract wheel contains unapproved EIOS content")
        if any(".data/" in item for item in names):
            raise ValueError("Input-contract wheel contains unapproved data")
        metadata = [
            item for item in names
            if item.endswith(".dist-info/METADATA")
        ]
        if len(metadata) != 1 or not metadata[0].startswith("eios_input_contracts-0.1.0.dist-info/"):
            raise ValueError("Invalid input-contract METADATA path")
        lines = archive.read(metadata[0]).decode("utf-8").splitlines()
        if "Name: eios-input-contracts" not in lines or "Version: 0.1.0" not in lines:
            raise ValueError("Invalid input-contract distribution identity/version")
        requirements = [item for item in lines if item.startswith("Requires-Dist:")]
        declared = [
            re.match(r"Requires-Dist:\s*([A-Za-z0-9_-]+)", item).group(1).lower()
            for item in requirements
        ]
        if sorted(declared) != ["eios-kernel", "pydantic"]:
            raise ValueError("Only pinned kernel and Pydantic allowed")
        if not any("eios-kernel==0.1.0" in item.replace(" ", "") for item in requirements):
            raise ValueError("Exact neutral kernel dependency required")
        with tempfile.TemporaryDirectory(prefix="eios-input-wheel-audit-") as temp:
            audit_root = Path(temp)
            for rel in SOURCE_FILES:
                target = audit_root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(rel.as_posix()))
            verify_source_dependencies(audit_root)


def build(output: Path, root: Path = ROOT) -> Path:
    with tempfile.TemporaryDirectory(prefix="eios-input-build-") as tmp:
        base = Path(tmp)
        staged, wheels = base / "source", base / "wheels"
        stage_distribution(staged, root)
        wheels.mkdir()
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps",
             "--no-build-isolation", "--wheel-dir", str(wheels), str(staged)],
            check=True,
        )
        candidates = list(wheels.glob("eios_input_contracts-*.whl"))
        if len(candidates) != 1:
            raise ValueError("Expected one neutral input-contract wheel")
        audit_wheel(candidates[0])
        output.mkdir(parents=True, exist_ok=True)
        final = output / candidates[0].name
        shutil.copy2(candidates[0], final)
        return final


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/inputs"))
    args = parser.parse_args()
    print(f"Audited neutral input wheel: {build(args.output.resolve())}")


if __name__ == "__main__":
    main()
