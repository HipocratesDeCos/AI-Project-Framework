"""Build an OPTIONAL procurement PRICE wheel from the ONE existing source tree.

PRICE C1 includes its public package __init__, documentary company coverage,
HIS003 and all pricing carrier contracts. Its input depends on PurchaseOperation
in eios.core.models; this is not a generic sales price authority.
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
METADATA_FILE = Path("packaging/eios-price-procurement/pyproject.toml")
SOURCE_FILES = (
    Path("eios/core/validation.py"),
    Path("eios/pricing/__init__.py"),
    Path("eios/pricing/aggregation.py"),
    Path("eios/pricing/company_coverage.py"),
    Path("eios/pricing/comparable_reference.py"),
    Path("eios/pricing/critical_baseline.py"),
    Path("eios/pricing/engine.py"),
    Path("eios/pricing/historical_comparability.py"),
    Path("eios/pricing/historical_reference.py"),
    Path("eios/pricing/models.py"),
    Path("eios/pricing/recommended_ceiling.py"),
    Path("eios/pricing/representativeness.py"),
    Path("eios/pricing/sufficiency.py"),
)
DISTRIBUTION = "eios-price-procurement"
PACKAGE_VERSION = "0.2.0"
ALLOWED_INTERNAL_MODULES = frozenset({"eios.core.models"}) | frozenset(
    str(relative.with_suffix("")).replace("/", ".").removesuffix(".__init__")
    for relative in SOURCE_FILES
)


def verify_source_dependencies(root: Path = ROOT) -> None:
    """Refuse any internal EIOS import not shipped in this exact distribution."""
    for relative in SOURCE_FILES:
        source = (root / relative).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(relative))
        package = ".".join(relative.parts[:-1])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                dependencies = (item.name for item in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 1:
                    raise ValueError(f"Forbidden parent-relative import: {relative}")
                if node.level == 1:
                    if node.module:
                        dependencies = (f"{package}.{node.module}",)
                    else:
                        dependencies = (
                            f"{package}.{item.name}" for item in node.names
                        )
                else:
                    dependencies = (node.module or "",)
            else:
                continue
            for name in dependencies:
                if name == "eios" or name.startswith("eios."):
                    if name not in ALLOWED_INTERNAL_MODULES:
                        raise ValueError(
                            f"Forbidden unbundled EIOS import in {relative}: {name}"
                        )


def stage_distribution(destination: Path, root: Path = ROOT) -> None:
    verify_source_dependencies(root)
    stage = destination / "src"
    stage.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / METADATA_FILE, destination / "pyproject.toml")
    for path in SOURCE_FILES:
        staged = stage / path
        staged.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / path, staged)


def audit_wheel(wheel: Path) -> None:
    """Reject extra modules/data/dependencies by inspecting real wheel bytes."""
    with zipfile.ZipFile(wheel) as archive:
        raw_names = archive.namelist()
        if len(raw_names) != len(set(raw_names)):
            raise ValueError("Duplicate ZIP names forbidden")
        names = set(raw_names)
        expected = {file.as_posix() for file in SOURCE_FILES}
        actual_python = {item for item in names if item.endswith(".py")}
        if actual_python != expected:
            raise ValueError(
                f"Unexpected PRICE Python modules: {sorted(actual_python ^ expected)}"
            )
        if any(name.startswith("eios/") and name not in expected for name in names):
            raise ValueError("PRICE wheel includes unapproved EIOS content")
        if any(".data/" in name for name in names):
            raise ValueError("PRICE wheel includes unapproved wheel data")
        info = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(info) != 1 or not info[0].startswith("eios_price_procurement-0.2.0.dist-info/"):
            raise ValueError("Expected one PRICE distribution METADATA")
        lines = archive.read(info[0]).decode("utf-8").splitlines()
        if "Name: eios-price-procurement" not in lines:
            raise ValueError("Wrong PRICE distribution name")
        if "Version: 0.2.0" not in lines:
            raise ValueError("Wrong PRICE distribution version")
        deps = [line for line in lines if line.startswith("Requires-Dist:")]
        names = [
            re.match(r"Requires-Dist:\s*([A-Za-z0-9_-]+)", item).group(1).lower()
            for item in deps
        ]
        if sorted(names) != ["eios-contracts-procurement", "pydantic"]:
            raise ValueError("PRICE wheel must depend on Pydantic and shared C0 contracts only")
        if not any("eios-contracts-procurement==0.1.0" in item.replace(" ", "") for item in deps):
            raise ValueError("PRICE wheel must pin exact shared C0 contract version")
        # Confirm the staged module graph, not only the repository imports.
        with tempfile.TemporaryDirectory(prefix="eios-price-wheel-audit-") as audit_dir:
            audit_root = Path(audit_dir)
            for name in expected:
                path = audit_root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(name))
            verify_source_dependencies(audit_root)


def build(output: Path, root: Path = ROOT) -> Path:
    with tempfile.TemporaryDirectory(prefix="eios-price-build-") as work:
        workspace = Path(work)
        staging = workspace / "staging"
        wheels = workspace / "wheels"
        stage_distribution(staging, root)
        wheels.mkdir()
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps",
             "--no-build-isolation", "--wheel-dir", str(wheels), str(staging)],
            check=True,
        )
        found = list(wheels.glob("eios_price_procurement-*.whl"))
        if len(found) != 1:
            raise ValueError("Expected exactly one optional PRICE wheel")
        audit_wheel(found[0])
        output.mkdir(parents=True, exist_ok=True)
        destination = output / found[0].name
        shutil.copy2(found[0], destination)
        return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/price"))
    options = parser.parse_args()
    wheel = build(options.output.resolve())
    print(f"Audited optional PRICE wheel: {wheel}")


if __name__ == "__main__":
    main()
