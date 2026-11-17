"""F5.5: C0 model is shipped exactly once and capability wheels depend on it."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tomllib
import zipfile

import pytest

from tools.build_eios_contracts_distribution import (
    SOURCE_FILES as CONTRACT_SOURCES,
    METADATA_FILE as CONTRACT_META,
    audit_wheel as audit_contracts,
    stage_distribution,
    verify_source_dependencies,
)
from tools.build_eios_price_distribution import SOURCE_FILES as PRICE_SOURCES
from tools.build_eios_tco_distribution import SOURCE_FILES as TCO_SOURCES
from tools.build_eios_kernel_distribution import SOURCE_FILES as KERNEL_SOURCES
from tools.verify_f5_5_shared_contracts import owned_paths, verify_payloads

ROOT = Path(__file__).resolve().parents[1]


def test_shared_contracts_have_a_single_canonical_owner():
    shared = Path("eios/core/models.py")
    assert set(CONTRACT_SOURCES) == {shared}
    assert shared not in PRICE_SOURCES
    assert shared not in TCO_SOURCES
    assert shared not in KERNEL_SOURCES
    assert not set(PRICE_SOURCES) & set(TCO_SOURCES)
    assert not set(KERNEL_SOURCES) & set(CONTRACT_SOURCES)
    verify_source_dependencies()


def test_shared_contracts_staging_copies_canonical_source_byte_for_byte(tmp_path):
    stage_distribution(tmp_path)
    found = {
        x.relative_to(tmp_path / "src")
        for x in (tmp_path / "src").rglob("*.py")
    }
    assert found == {Path("eios/core/models.py")}
    assert (tmp_path / "src/eios/core/models.py").read_bytes() == (
        ROOT / "eios/core/models.py"
    ).read_bytes()
    assert not (tmp_path / "src/eios/core/__init__.py").exists()


def test_metadata_constrains_versions_and_declares_true_shared_dependency():
    contracts = tomllib.loads((ROOT / CONTRACT_META).read_text(encoding="utf-8"))
    price = tomllib.loads((ROOT / "packaging/eios-price-procurement/pyproject.toml").read_text(encoding="utf-8"))
    tco = tomllib.loads((ROOT / "packaging/eios-tco-procurement/pyproject.toml").read_text(encoding="utf-8"))
    assert contracts["project"]["name"] == "eios-contracts-procurement"
    assert contracts["project"]["version"] == "0.1.0"
    assert contracts["project"]["dependencies"] == ["pydantic>=2.0,<3.0"]
    for capability, name in ((price, "price"), (tco, "tco")):
        assert capability["project"]["version"] == "0.2.0"
        assert capability["project"]["dependencies"] == [
            "pydantic>=2.0,<3.0", "eios-contracts-procurement==0.1.0",
        ]
    full = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert full["project"]["name"] == "eios-mvp"


@pytest.mark.parametrize("illegal", (
    "from eios.pricing.engine import run_price_intelligence",
    "import eios.tco.engine",
    "from .validation import validate_evidence",
    "from eios.kernel.execution import execute_kernel",
))
def test_shared_model_cannot_acquire_dependencies_on_business_modules(tmp_path, illegal):
    rel = Path("eios/core/models.py")
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(illegal + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="independent|relative"):
        verify_source_dependencies(tmp_path)


def _fake_contracts(wheel, *, extra=(), metadata=(
    "Metadata-Version: 2.3\nName: eios-contracts-procurement\n"
    "Version: 0.1.0\nRequires-Dist: pydantic>=2,<3\n"
)):
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("eios/core/models.py", "# harmless synthetic test\n")
        for name in extra:
            archive.writestr(name, "# unauthorized extra\n")
        archive.writestr(
            "eios_contracts_procurement-0.1.0.dist-info/METADATA",
            metadata,
        )


def test_contracts_audit_accepts_exact_wheel_and_blocks_unwanted_modules(tmp_path):
    wheel = tmp_path / "contracts.whl"
    _fake_contracts(wheel)
    audit_contracts(wheel)
    assert owned_paths(wheel) == {"eios/core/models.py"}
    for extra in ("eios/pricing/engine.py", "eios/core/validation.py", "eios/__init__.py"):
        _fake_contracts(wheel, extra=(extra,))
        with pytest.raises(ValueError, match="Wrong|unapproved"):
            audit_contracts(wheel)


def test_contracts_audit_blocks_unapproved_dependency_and_import(tmp_path):
    wheel = tmp_path / "contracts.whl"
    _fake_contracts(wheel, metadata=(
        "Name: eios-contracts-procurement\nVersion: 0.1.0\n"
        "Requires-Dist: pydantic>=2,<3\nRequires-Dist: openpyxl>=3\n"
    ))
    with pytest.raises(ValueError, match="Pydantic"):
        audit_contracts(wheel)
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("eios/core/models.py", "from eios.pricing.engine import run_price_intelligence\n")
        archive.writestr(
            "eios_contracts_procurement-0.1.0.dist-info/METADATA",
            "Name: eios-contracts-procurement\nVersion: 0.1.0\n"
            "Requires-Dist: pydantic>=2,<3\n",
        )
    with pytest.raises(ValueError, match="independent"):
        audit_contracts(wheel)


def test_five_five_verifier_rejects_any_duplicate_physical_module(tmp_path):
    # Adversarial: unlike an ordinary metadata check, inspect file ownership.
    from tools.verify_f5_5_shared_contracts import WHEEL_NAMES
    wheels = {}
    for name in WHEEL_NAMES:
        file = tmp_path / (name + ".whl")
        with zipfile.ZipFile(file, "w") as archive:
            archive.writestr(
                "eios/core/models.py" if name != "eios-kernel"
                else "eios/kernel/execution.py",
                "source",
            )
        wheels[name] = file
    with pytest.raises(ValueError):
        verify_payloads(wheels)


def test_f5_5_command_line_uses_the_real_dir_destinations(tmp_path):
    """Guard CLI plumbing before any expensive wheel installations."""
    runner = ROOT / "tools/verify_f5_5_shared_contracts.py"
    result = subprocess.run(
        [sys.executable, str(runner), "--kernel-dir", str(tmp_path),
         "--contracts-dir", str(tmp_path), "--price-dir", str(tmp_path),
         "--tco-dir", str(tmp_path)],
        cwd=tmp_path, capture_output=True, text=True, timeout=15,
    )
    assert result.returncode != 0
    assert "Expected one wheel for eios-kernel" in (result.stdout + result.stderr)
    assert "AttributeError" not in (result.stdout + result.stderr)
