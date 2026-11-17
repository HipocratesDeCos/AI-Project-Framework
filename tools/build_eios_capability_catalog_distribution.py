"""F5.7 — build the independently installable, audited neutral capability catalog."""
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
METADATA_FILE = Path("packaging/eios-capability-catalog/pyproject.toml")
SOURCE_FILES = (
    Path("eios/capability_catalog/__init__.py"),
    Path("eios/capability_catalog/catalog.py"),
)
ALLOWED_INTERNAL_IMPORTS = frozenset({
    "eios.capability_catalog.catalog",
    "eios.kernel.execution",
    "eios.input_contracts",
})
REQUIRED_DEPENDENCIES = {
    "pydantic": None,
    "eios-kernel": "0.1.0",
    "eios-input-contracts": "0.1.0",
}


def verify_source_dependencies(root: Path = ROOT) -> None:
    for rel in SOURCE_FILES:
        parent_module = ".".join(rel.parts[:-1])
        tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=str(rel))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports = (alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 1:
                    raise ValueError(f"Forbidden parent-relative EIOS import in {rel}")
                if node.level == 1:
                    if not node.module:
                        raise ValueError(f"Forbidden ambiguous EIOS relative import in {rel}")
                    imports = (f"{parent_module}.{node.module}",)
                else:
                    imports = (node.module or "",)
            else:
                continue
            for name in imports:
                if (name == "eios" or name.startswith("eios.")) and (
                    name not in ALLOWED_INTERNAL_IMPORTS
                ):
                    raise ValueError(f"Forbidden business dependency: {rel}: {name}")


def stage_distribution(destination: Path, root: Path = ROOT) -> None:
    verify_source_dependencies(root)
    (destination / "src").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / METADATA_FILE, destination / "pyproject.toml")
    for rel in SOURCE_FILES:
        target = destination / "src" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, target)


def audit_wheel(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        listed = archive.namelist()
        names = set(listed)
        if len(names) != len(listed):
            raise ValueError("Duplicate capability catalog ZIP paths")
        approved = {rel.as_posix() for rel in SOURCE_FILES}
        if {name for name in names if name.endswith(".py")} != approved:
            raise ValueError("Unexpected Python modules in capability catalog wheel")
        if any(name.startswith("eios/") and name not in approved for name in names):
            raise ValueError("Unapproved EIOS content in catalog wheel")
        if any(".data/" in name for name in names):
            raise ValueError("Unapproved catalog wheel data")
        metas = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metas) != 1 or not metas[0].startswith("eios_capability_catalog-0.1.0.dist-info/"):
            raise ValueError("Invalid catalog distribution METADATA path")
        lines = archive.read(metas[0]).decode("utf-8").splitlines()
        if "Name: eios-capability-catalog" not in lines or "Version: 0.1.0" not in lines:
            raise ValueError("Invalid catalog distribution identity")
        deps = [line for line in lines if line.startswith("Requires-Dist:")]
        parsed = {}
        for item in deps:
            m = re.match(r"Requires-Dist:\s*([A-Za-z0-9_-]+)", item)
            if m is None:
                raise ValueError("Invalid catalog dependency")
            key = m.group(1).lower().replace("_", "-")
            if key in parsed:
                raise ValueError("Duplicate catalog dependency")
            parsed[key] = item
        if set(parsed) != set(REQUIRED_DEPENDENCIES):
            raise ValueError("Catalog must depend on Pydantic, kernel and input contracts only")
        for name, pinned in REQUIRED_DEPENDENCIES.items():
            item = parsed[name].replace(" ", "")
            if pinned is not None and f"{name}=={pinned}" not in item.lower().replace("_", "-"):
                raise ValueError(f"Exact {name} dependency required")
        with tempfile.TemporaryDirectory(prefix="eios-catalog-audit-") as tmp:
            audit_root = Path(tmp)
            for rel in SOURCE_FILES:
                target = audit_root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(rel.as_posix()))
            verify_source_dependencies(audit_root)


def build(output: Path, root: Path = ROOT) -> Path:
    with tempfile.TemporaryDirectory(prefix="eios-catalog-build-") as temp:
        base = Path(temp)
        stage, wheels = base / "source", base / "wheels"
        stage_distribution(stage, root)
        wheels.mkdir()
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps",
             "--no-build-isolation", "--wheel-dir", str(wheels), str(stage)],
            check=True,
        )
        candidates = list(wheels.glob("eios_capability_catalog-*.whl"))
        if len(candidates) != 1:
            raise ValueError("Expected exactly one audited catalog wheel")
        audit_wheel(candidates[0])
        output.mkdir(parents=True, exist_ok=True)
        destination = output / candidates[0].name
        shutil.copy2(candidates[0], destination)
        return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/catalog"))
    arguments = parser.parse_args()
    print(f"Audited independent capability catalog wheel: {build(arguments.output.resolve())}")


if __name__ == "__main__":
    main()
