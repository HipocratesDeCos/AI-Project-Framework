"""F5.6: the neutral inputs wheel is auditable and has no domain dependencies."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tomllib
import zipfile

import pytest

from tools.build_eios_input_contracts_distribution import (
    ALLOWED_IMPORTS, METADATA_FILE, ROOT, SOURCE_FILES,
    audit_wheel, stage_distribution, verify_source_dependencies,
)
from tools.build_eios_kernel_distribution import SOURCE_FILES as KERNEL_SOURCES
from tools.build_eios_contracts_distribution import SOURCE_FILES as C0_SOURCES
from tools.build_eios_price_distribution import SOURCE_FILES as PRICE_SOURCES
from tools.build_eios_tco_distribution import SOURCE_FILES as TCO_SOURCES

APPROVED = {
    Path("eios/input_contracts/__init__.py"),
    Path("eios/input_contracts/contracts.py"),
}


def test_only_neutral_boundary_and_kernel_imports_are_allowed():
    assert set(SOURCE_FILES) == APPROVED
    assert ALLOWED_IMPORTS == {
        "eios.input_contracts.contracts",
        "eios.kernel.execution",
    }
    verify_source_dependencies()
    for domain in (C0_SOURCES, PRICE_SOURCES, TCO_SOURCES, KERNEL_SOURCES):
        assert APPROVED.isdisjoint(domain)
    metadata = tomllib.loads((ROOT / METADATA_FILE).read_text(encoding="utf-8"))
    assert metadata["project"]["name"] == "eios-input-contracts"
    assert metadata["project"]["version"] == "0.1.0"
    assert metadata["project"]["dependencies"] == [
        "pydantic>=2.0,<3.0", "eios-kernel==0.1.0",
    ]
    assert metadata["tool"]["setuptools"]["packages"]["find"]["namespaces"] is True


def test_staging_copies_both_sources_byte_for_byte_and_no_business_modules(tmp_path):
    stage_distribution(tmp_path)
    files = {
        path.relative_to(tmp_path / "src")
        for path in (tmp_path / "src").rglob("*.py")
    }
    assert files == APPROVED
    for rel in SOURCE_FILES:
        assert (tmp_path / "src" / rel).read_bytes() == (ROOT / rel).read_bytes()
    assert not (tmp_path / "src/eios/core/models.py").exists()
    assert not (tmp_path / "src/eios/kernel/execution.py").exists()
    assert not (tmp_path / "src/eios/pricing/engine.py").exists()


@pytest.mark.parametrize("injected", (
    "from eios.core.models import PurchaseOperation",
    "from eios.pricing.engine import run_price_intelligence",
    "import eios.tco.engine",
    "from eios.quality.gate import evaluate_quality",
    "from .fictitious_module import run",
    "from ..core.models import PurchaseOperation",
))
def test_new_domain_dependency_fails_closed(tmp_path, injected):
    for rel in SOURCE_FILES:
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / rel).read_bytes())
    target = tmp_path / "eios/input_contracts/contracts.py"
    target.write_text(target.read_text(encoding="utf-8") + "\n" + injected + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Forbidden"):
        verify_source_dependencies(tmp_path)


def _fake_wheel(wheel, *, extras=(), deps=(
    "Requires-Dist: pydantic>=2,<3",
    "Requires-Dist: eios-kernel==0.1.0",
)):
    with zipfile.ZipFile(wheel, "w") as archive:
        for rel in SOURCE_FILES:
            archive.writestr(rel.as_posix(), "# synthetic wheel module\n")
        for path in extras:
            archive.writestr(path, "# invalid extra\n")
        archive.writestr(
            "eios_input_contracts-0.1.0.dist-info/METADATA",
            "Metadata-Version: 2.3\nName: eios-input-contracts\nVersion: 0.1.0\n"
            + "\n".join(deps) + "\n",
        )


def test_wheel_audit_accepts_exact_files_and_pin(tmp_path):
    wheel = tmp_path / "fake.whl"
    _fake_wheel(wheel)
    audit_wheel(wheel)


@pytest.mark.parametrize("extra", (
    "eios/core/models.py",
    "eios/kernel/execution.py",
    "eios/input_contracts/accidental.py",
    "eios/input_contracts/__pycache__/contracts.pyc",
    "eios/input_contracts/local_secrets.json",
))
def test_wheel_audit_rejects_unapproved_payload(tmp_path, extra):
    wheel = tmp_path / "fake.whl"
    _fake_wheel(wheel, extras=(extra,))
    with pytest.raises(ValueError, match="Unexpected|unapproved"):
        audit_wheel(wheel)


def test_wheel_requires_exact_kernel_pin_and_no_database_or_excel_dependency(tmp_path):
    wheel = tmp_path / "fake.whl"
    _fake_wheel(wheel, deps=("Requires-Dist: pydantic>=2,<3",))
    with pytest.raises(ValueError, match="Only pinned kernel"):
        audit_wheel(wheel)
    _fake_wheel(wheel, deps=(
        "Requires-Dist: pydantic>=2,<3", "Requires-Dist: eios-kernel>=0.1.0",
    ))
    with pytest.raises(ValueError, match="Exact neutral kernel"):
        audit_wheel(wheel)
    _fake_wheel(wheel, deps=(
        "Requires-Dist: pydantic>=2,<3", "Requires-Dist: eios-kernel==0.1.0",
        "Requires-Dist: openpyxl>=3",
    ))
    with pytest.raises(ValueError, match="Only pinned kernel"):
        audit_wheel(wheel)


def test_wheel_rejects_injected_business_import_even_without_extra_file(tmp_path):
    wheel = tmp_path / "fake.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("eios/input_contracts/__init__.py", "# fixture\n")
        archive.writestr("eios/input_contracts/contracts.py", "import eios.pricing.engine\n")
        archive.writestr(
            "eios_input_contracts-0.1.0.dist-info/METADATA",
            "Name: eios-input-contracts\nVersion: 0.1.0\n"
            "Requires-Dist: pydantic>=2,<3\n"
            "Requires-Dist: eios-kernel==0.1.0\n",
        )
    with pytest.raises(ValueError, match="Forbidden"):
        audit_wheel(wheel)


def test_build_command_line_checks_missing_wheel_dir_without_crashing(tmp_path):
    runner = ROOT / "tools/verify_f5_6_two_domains.py"
    if not runner.is_file():
        pytest.fail("Expected F5.6 isolated domain verifier")
    completed = subprocess.run(
        [sys.executable, str(runner),
         "--kernel-dir", str(tmp_path),
         "--inputs-dir", str(tmp_path),
         "--contracts-dir", str(tmp_path),
         "--price-dir", str(tmp_path),
         "--tco-dir", str(tmp_path)],
        cwd=tmp_path, capture_output=True, text=True, timeout=15,
    )
    assert completed.returncode != 0
    assert "Expected exactly one wheel for eios-kernel" in completed.stdout + completed.stderr
    assert "AttributeError" not in completed.stdout + completed.stderr
