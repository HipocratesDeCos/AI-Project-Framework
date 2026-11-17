"""F5.8 — build an isolated governance wheel from exactly canonical source."""
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
METADATA_FILE = Path("packaging/eios-catalog-governance/pyproject.toml")
SOURCE_FILES = (
    Path("eios/catalog_governance/__init__.py"),
    Path("eios/catalog_governance/ledger.py"),
)
ALLOWED_INTERNAL_IMPORTS = frozenset({
    "eios.catalog_governance.ledger",
    "eios.capability_catalog",
    "eios.input_contracts",
    "eios.kernel.execution",
})
EXPECTED_REQUIREMENTS = {
    "pydantic": None,
    "eios-kernel": "0.1.0",
    "eios-input-contracts": "0.1.0",
    "eios-capability-catalog": "0.1.0",
}


def verify_source_dependencies(root: Path = ROOT) -> None:
    for relative in SOURCE_FILES:
        package = ".".join(relative.parts[:-1])
        tree = ast.parse(
            (root / relative).read_text(encoding="utf-8"),
            filename=str(relative),
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports = (part.name for part in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 1 or (node.level == 1 and not node.module):
                    raise ValueError(f"Forbidden relative module in {relative}")
                imports = (
                    f"{package}.{node.module}" if node.level else node.module or "",
                )
            else:
                continue
            for imported in imports:
                if (imported == "eios" or imported.startswith("eios.")) and (
                    imported not in ALLOWED_INTERNAL_IMPORTS
                ):
                    raise ValueError(f"Forbidden EIOS domain dependency: {relative}: {imported}")


def stage_distribution(destination: Path, root: Path = ROOT) -> None:
    verify_source_dependencies(root)
    (destination / "src").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / METADATA_FILE, destination / "pyproject.toml")
    for relative in SOURCE_FILES:
        output = destination / "src" / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / relative, output)


def audit_wheel(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as zip_file:
        entries = zip_file.namelist()
        names = set(entries)
        if len(names) != len(entries):
            raise ValueError("Duplicate wheel ZIP members")
        expected = {relative.as_posix() for relative in SOURCE_FILES}
        if {name for name in names if name.endswith(".py")} != expected:
            raise ValueError("Unexpected governance Python module")
        if any(name.startswith("eios/") and name not in expected for name in names):
            raise ValueError("Governance wheel contains unapproved EIOS content")
        if any(".data/" in name for name in names):
            raise ValueError("Governance wheel contains unexpected data")
        metadatas = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadatas) != 1 or not metadatas[0].startswith(
            "eios_catalog_governance-0.1.0.dist-info/"
        ):
            raise ValueError("Unexpected governance metadata path")
        lines = zip_file.read(metadatas[0]).decode("utf-8").splitlines()
        if "Name: eios-catalog-governance" not in lines or "Version: 0.1.0" not in lines:
            raise ValueError("Incorrect governance wheel name/version")
        declared: dict[str, str] = {}
        for line in lines:
            if not line.startswith("Requires-Dist:"):
                continue
            found = re.match(r"Requires-Dist:\s*([A-Za-z0-9_-]+)", line)
            if found is None:
                raise ValueError("Invalid governance wheel dependency")
            key = found.group(1).lower().replace("_", "-")
            if key in declared:
                raise ValueError("Duplicate governance wheel dependency")
            declared[key] = line.lower().replace(" ", "").replace("_", "-")
        if set(declared) != set(EXPECTED_REQUIREMENTS):
            raise ValueError("Unapproved governance wheel dependency set")
        for name, version in EXPECTED_REQUIREMENTS.items():
            if version is not None and f"{name}=={version}" not in declared[name]:
                raise ValueError(f"Missing exact dependency pin: {name}")
        with tempfile.TemporaryDirectory(prefix="eios-f5-8-wheel-audit-") as work:
            stage = Path(work)
            for relative in SOURCE_FILES:
                output = stage / relative
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(zip_file.read(relative.as_posix()))
            verify_source_dependencies(stage)


def build(output_dir: Path, root: Path = ROOT) -> Path:
    with tempfile.TemporaryDirectory(prefix="eios-f5-8-wheel-build-") as temporary:
        work = Path(temporary)
        source, wheels = work / "source", work / "wheels"
        stage_distribution(source, root)
        wheels.mkdir()
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps",
             "--no-build-isolation", "--wheel-dir", str(wheels), str(source)],
            check=True,
        )
        found = list(wheels.glob("eios_catalog_governance-*.whl"))
        if len(found) != 1:
            raise ValueError("Expected exactly one governance distribution")
        audit_wheel(found[0])
        output_dir.mkdir(parents=True, exist_ok=True)
        dest = output_dir / found[0].name
        shutil.copy2(found[0], dest)
        return dest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/governance"))
    arguments = parser.parse_args()
    print(f"Audited F5.8 governance wheel: {build(arguments.output.resolve())}")


if __name__ == "__main__":
    main()
