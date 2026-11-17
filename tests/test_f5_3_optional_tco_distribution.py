"""F5.3: package exact canonical procurement TCO code, not a forked formula."""
from __future__ import annotations

from pathlib import Path
import tomllib
import zipfile

import pytest

from tools.build_eios_tco_distribution import (
    METADATA_FILE, SOURCE_FILES, audit_wheel, stage_distribution,
    verify_source_dependencies,
)
from tools.verify_f5_3_optional_tco import wheel_hashes

ROOT = Path(__file__).resolve().parents[1]
APPROVED = {
    Path("eios/tco/__init__.py"),
    Path("eios/tco/models.py"),
    Path("eios/tco/engine.py"),
}


def test_manifest_does_not_replace_or_install_general_eios_application():
    assert set(SOURCE_FILES) == APPROVED
    verify_source_dependencies()
    manifest = tomllib.loads((ROOT / METADATA_FILE).read_text(encoding="utf-8"))
    assert manifest["project"]["name"] == "eios-tco-procurement"
    assert manifest["project"]["version"] == "0.2.0"
    assert manifest["project"]["dependencies"] == ["pydantic>=2.0,<3.0", "eios-contracts-procurement==0.1.0"]
    assert manifest["tool"]["setuptools"]["packages"]["find"]["namespaces"] is True
    old = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert old["project"]["name"] == "eios-mvp"
    assert "openpyxl>=3.1,<4.0" in old["project"]["dependencies"]


def test_staging_is_exact_and_does_not_duplicate_tco_implementation(tmp_path):
    stage_distribution(tmp_path)
    found = {
        path.relative_to(tmp_path / "src")
        for path in (tmp_path / "src").rglob("*.py")
    }
    assert found == APPROVED
    for path in SOURCE_FILES:
        assert (tmp_path / "src" / path).read_bytes() == (ROOT / path).read_bytes()
    assert not (tmp_path / "src" / "eios/kernel/execution.py").exists()
    assert not (tmp_path / "src" / "eios/core/execution_boundary.py").exists()
    assert not (tmp_path / "src" / "eios/company_app.py").exists()
    assert not (tmp_path / "src" / "eios/core/__init__.py").exists()


@pytest.mark.parametrize("illegal", (
    "import eios.company_finance_parameters",
    "from eios.core.execution_boundary import execute_plan",
    "from eios.kernel.execution import execute_kernel",
    "from .future_rules import unknown",
    "from ..company_app import start",
))
def test_unbundled_dependency_fails_closed(tmp_path, illegal):
    for path in SOURCE_FILES:
        f = tmp_path / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("# fixture\n", encoding="utf-8")
    target = tmp_path / "eios/tco/engine.py"
    target.write_text(illegal + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Forbidden"):
        verify_source_dependencies(tmp_path)


def _fake_wheel(output, source_files, *, requirements=(
    "Requires-Dist: pydantic>=2,<3",
    "Requires-Dist: eios-contracts-procurement==0.1.0",
)):
    with zipfile.ZipFile(output, "w") as archive:
        for source in source_files:
            archive.writestr(source, "# synthetic test code\n")
        archive.writestr(
            "eios_tco_procurement-0.2.0.dist-info/METADATA",
            "Metadata-Version: 2.2\nName: eios-tco-procurement\nVersion: 0.2.0\n"
            + "\n".join(requirements) + "\n",
        )


def test_audit_accepts_exact_payload_and_returns_individual_hashes(tmp_path):
    wheel = tmp_path / "synthetic.whl"
    _fake_wheel(wheel, {p.as_posix() for p in APPROVED})
    audit_wheel(wheel)
    hashes = wheel_hashes(wheel)
    assert set(hashes) == {p.as_posix() for p in APPROVED}
    assert all(len(value) == 64 for value in hashes.values())


@pytest.mark.parametrize("extra", (
    "eios/company_app.py",
    "eios/kernel/execution.py",
    "eios/tco/__pycache__/engine.pyc",
))
def test_audit_rejects_unapproved_package_content(tmp_path, extra):
    wheel = tmp_path / "synthetic.whl"
    sources = {p.as_posix() for p in APPROVED} | {extra}
    _fake_wheel(wheel, sources)
    with pytest.raises(ValueError, match="Unexpected|beyond"):
        audit_wheel(wheel)


def test_audit_rejects_missing_engine_or_additional_excel_dependency(tmp_path):
    wheel = tmp_path / "synthetic.whl"
    paths = {p.as_posix() for p in APPROVED}
    _fake_wheel(wheel, paths - {"eios/tco/engine.py"})
    with pytest.raises(ValueError, match="Unexpected"):
        audit_wheel(wheel)
    _fake_wheel(
        wheel, paths, requirements=(
            "Requires-Dist: pydantic>=2,<3", "Requires-Dist: openpyxl>=3",
        ),
    )
    with pytest.raises(ValueError, match="Pydantic and shared C0"):
        audit_wheel(wheel)


def test_canonical_tco_engine_keeps_its_single_existing_function():
    from eios.tco.engine import calculate_tco

    assert callable(calculate_tco)
    source = (ROOT / "eios/tco/engine.py").read_text(encoding="utf-8")
    assert source.count("def calculate_tco(") == 1
    assert "operation.quantity * operation.unit_price" in source
