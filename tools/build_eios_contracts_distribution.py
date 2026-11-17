"""F5.5: package the ONLY canonical procurement C0 contracts module.

Builds from eios/core/models.py unchanged, via an ephemeral PEP 517 stage.
Other capability distributions must depend on this unique path owner rather
than bundling a duplicate of models.py. This is not a generic business schema.
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
METADATA_FILE = Path("packaging/eios-contracts-procurement/pyproject.toml")
SOURCE_FILES = (Path("eios/core/models.py"),)
VERSION = "0.1.0"


def verify_source_dependencies(root: Path = ROOT) -> None:
    for rel in SOURCE_FILES:
        tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=str(rel))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = (entry.name for entry in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    raise ValueError("C0 contracts cannot import relative EIOS modules")
                modules = (node.module or "",)
            else:
                continue
            for module in modules:
                if module == "eios" or module.startswith("eios."):
                    raise ValueError(f"Contracts must be independent: {module}")


def stage_distribution(destination: Path, root: Path = ROOT) -> None:
    verify_source_dependencies(root)
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
            raise ValueError("Duplicate wheel ZIP names")
        expected = {rel.as_posix() for rel in SOURCE_FILES}
        if {x for x in names if x.endswith(".py")} != expected:
            raise ValueError("Wrong contracts Python modules")
        if any(x.startswith("eios/") and x not in expected for x in names):
            raise ValueError("Contracts wheel contains unapproved EIOS content")
        if any(".data/" in x for x in names):
            raise ValueError("Contracts wheel contains unapproved data")
        metas = [x for x in names if x.endswith(".dist-info/METADATA")]
        if len(metas) != 1 or not metas[0].startswith("eios_contracts_procurement-0.1.0.dist-info/"):
            raise ValueError("Wrong contracts METADATA path")
        lines = archive.read(metas[0]).decode("utf-8").splitlines()
        if "Name: eios-contracts-procurement" not in lines or "Version: 0.1.0" not in lines:
            raise ValueError("Wrong contracts identity/version")
        deps = [x for x in lines if x.startswith("Requires-Dist:")]
        if len(deps) != 1 or not re.fullmatch(
            r"Requires-Dist:\s*pydantic\s*(?:\([^)]*\)|[<>=!~,0-9. ]+)(?:\s*;.*)?",
            deps[0], re.IGNORECASE,
        ):
            raise ValueError("Contracts wheel depends only on Pydantic")
        with tempfile.TemporaryDirectory(prefix="eios-contracts-audit-") as tmp:
            root = Path(tmp)
            for rel in SOURCE_FILES:
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(rel.as_posix()))
            verify_source_dependencies(root)


def build(output: Path, root: Path = ROOT) -> Path:
    with tempfile.TemporaryDirectory(prefix="eios-contracts-build-") as tmp:
        workspace = Path(tmp)
        staged, wheels = workspace / "source", workspace / "wheels"
        stage_distribution(staged, root)
        wheels.mkdir()
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps",
             "--no-build-isolation", "--wheel-dir", str(wheels), str(staged)],
            check=True,
        )
        found = list(wheels.glob("eios_contracts_procurement-*.whl"))
        if len(found) != 1:
            raise ValueError("Expected one contracts wheel")
        audit_wheel(found[0])
        output.mkdir(parents=True, exist_ok=True)
        destination = output / found[0].name
        shutil.copy2(found[0], destination)
        return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/contracts"))
    opts = parser.parse_args()
    print(f"Audited shared contracts wheel: {build(opts.output.resolve())}")


if __name__ == "__main__":
    main()
