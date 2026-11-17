"""F5.8 — wheel must contain exactly two canonical and neutral modules."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tomllib
import zipfile

import pytest

from tools.build_eios_catalog_governance_distribution import (
    ALLOWED_INTERNAL_IMPORTS, EXPECTED_REQUIREMENTS, METADATA_FILE,
    ROOT, SOURCE_FILES, audit_wheel, stage_distribution,
    verify_source_dependencies,
)
from tools.build_eios_kernel_distribution import SOURCE_FILES as KERNEL_FILES
from tools.build_eios_input_contracts_distribution import SOURCE_FILES as INPUT_FILES
from tools.build_eios_capability_catalog_distribution import SOURCE_FILES as CATALOG_FILES
from tools.build_eios_price_distribution import SOURCE_FILES as PRICE_FILES
from tools.build_eios_tco_distribution import SOURCE_FILES as TCO_FILES
from tools.build_eios_contracts_distribution import SOURCE_FILES as C0_FILES

EXPECTED = {
    Path("eios/catalog_governance/__init__.py"),
    Path("eios/catalog_governance/ledger.py"),
}


def test_metadata_and_graph_are_pinned_to_only_neutral_modules():
    assert set(SOURCE_FILES) == EXPECTED
    assert ALLOWED_INTERNAL_IMPORTS == {
        "eios.catalog_governance.ledger", "eios.capability_catalog",
        "eios.input_contracts", "eios.kernel.execution",
    }
    assert EXPECTED_REQUIREMENTS == {
        "pydantic": None, "eios-kernel": "0.1.0",
        "eios-input-contracts": "0.1.0",
        "eios-capability-catalog": "0.1.0",
    }
    for other in (KERNEL_FILES, INPUT_FILES, CATALOG_FILES, PRICE_FILES, TCO_FILES, C0_FILES):
        assert EXPECTED.isdisjoint(other)
    verify_source_dependencies(ROOT)
    config = tomllib.loads((ROOT / METADATA_FILE).read_text(encoding="utf-8"))
    assert config["project"]["name"] == "eios-catalog-governance"
    assert config["project"]["version"] == "0.1.0"
    assert config["project"]["dependencies"] == [
        "pydantic>=2.0,<3.0", "eios-kernel==0.1.0",
        "eios-input-contracts==0.1.0", "eios-capability-catalog==0.1.0",
    ]


def test_staging_is_identical_to_canonical_and_has_no_borrowed_modules(tmp_path):
    stage_distribution(tmp_path)
    found = {
        path.relative_to(tmp_path / "src")
        for path in (tmp_path / "src").rglob("*.py")
    }
    assert found == EXPECTED
    for path in EXPECTED:
        assert (tmp_path / "src" / path).read_bytes() == (ROOT / path).read_bytes()
    assert not (tmp_path / "src/eios/pricing/engine.py").exists()
    assert not (tmp_path / "src/eios/core/models.py").exists()


@pytest.mark.parametrize("illegal", (
    "import eios.company_app",
    "from eios.core.models import PurchaseOperation",
    "from eios.pricing.engine import run_price_intelligence",
    "from eios.tco.models import TCOInput",
    "from eios.rules.pricing import evaluate",
    "from .unknown import run",
    "from ..kernel.execution import execute_kernel",
))
def test_new_business_dependency_fails_closed(tmp_path, illegal):
    for path in EXPECTED:
        output = tmp_path / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes((ROOT / path).read_bytes())
    target = tmp_path / "eios/catalog_governance/ledger.py"
    target.write_text(target.read_text(encoding="utf-8") + "\n" + illegal + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Forbidden"):
        verify_source_dependencies(tmp_path)


def _fake_wheel(file, *, extras=(), dependencies=(
    "Requires-Dist: pydantic>=2,<3",
    "Requires-Dist: eios-kernel==0.1.0",
    "Requires-Dist: eios-input-contracts==0.1.0",
    "Requires-Dist: eios-capability-catalog==0.1.0",
)):
    with zipfile.ZipFile(file, "w") as archive:
        for path in EXPECTED:
            archive.writestr(path.as_posix(), "# synthetic allowed module\n")
        for extra in extras:
            archive.writestr(extra, "# unapproved payload\n")
        archive.writestr(
            "eios_catalog_governance-0.1.0.dist-info/METADATA",
            "Metadata-Version: 2.3\nName: eios-catalog-governance\n"
            "Version: 0.1.0\n" + "\n".join(dependencies) + "\n",
        )


def test_audit_accepts_exact_contents_and_pins(tmp_path):
    file = tmp_path / "governance.whl"
    _fake_wheel(file)
    audit_wheel(file)


@pytest.mark.parametrize("extra", (
    "eios/kernel/execution.py",
    "eios/input_contracts/contracts.py",
    "eios/capability_catalog/catalog.py",
    "eios/core/models.py",
    "eios/catalog_governance/unsafe.py",
    "eios/catalog_governance/configuration.json",
))
def test_wheel_rejects_unapproved_module_or_data(tmp_path, extra):
    file = tmp_path / "governance.whl"
    _fake_wheel(file, extras=(extra,))
    with pytest.raises(ValueError, match="Unexpected|unapproved"):
        audit_wheel(file)


@pytest.mark.parametrize("deps", (
    ("Requires-Dist: pydantic>=2,<3",),
    (
        "Requires-Dist: pydantic>=2,<3",
        "Requires-Dist: eios-kernel>=0.1.0",
        "Requires-Dist: eios-input-contracts==0.1.0",
        "Requires-Dist: eios-capability-catalog==0.1.0",
    ),
    (
        "Requires-Dist: pydantic>=2,<3",
        "Requires-Dist: eios-kernel==0.1.0",
        "Requires-Dist: eios-input-contracts==0.1.0",
        "Requires-Dist: eios-capability-catalog>=0.1.0",
    ),
    (
        "Requires-Dist: pydantic>=2,<3",
        "Requires-Dist: eios-kernel==0.1.0",
        "Requires-Dist: eios-input-contracts==0.1.0",
        "Requires-Dist: eios-capability-catalog==0.1.0",
        "Requires-Dist: openpyxl>=3",
    ),
))
def test_dependencies_require_exact_pin_and_no_business_library(tmp_path, deps):
    file = tmp_path / "governance.whl"
    _fake_wheel(file, dependencies=deps)
    with pytest.raises(ValueError, match="dependency"):
        audit_wheel(file)


def test_wheel_rejects_hidden_business_import_even_with_approved_files(tmp_path):
    file = tmp_path / "governance.whl"
    with zipfile.ZipFile(file, "w") as archive:
        archive.writestr("eios/catalog_governance/__init__.py", "# synthetic\n")
        archive.writestr("eios/catalog_governance/ledger.py", "import eios.pricing.engine\n")
        archive.writestr(
            "eios_catalog_governance-0.1.0.dist-info/METADATA",
            "Name: eios-catalog-governance\nVersion: 0.1.0\n"
            "Requires-Dist: pydantic>=2,<3\n"
            "Requires-Dist: eios-kernel==0.1.0\n"
            "Requires-Dist: eios-input-contracts==0.1.0\n"
            "Requires-Dist: eios-capability-catalog==0.1.0\n",
        )
    with pytest.raises(ValueError, match="Forbidden"):
        audit_wheel(file)


def test_cli_parses_all_directory_flags_before_attempting_install(tmp_path):
    runner = ROOT / "tools/verify_f5_8_governance_two_domains.py"
    assert runner.is_file()
    result = subprocess.run(
        [sys.executable, str(runner),
         "--kernel-dir", str(tmp_path), "--inputs-dir", str(tmp_path),
         "--catalog-dir", str(tmp_path), "--governance-dir", str(tmp_path),
         "--contracts-dir", str(tmp_path), "--price-dir", str(tmp_path),
         "--tco-dir", str(tmp_path)],
        cwd=tmp_path, capture_output=True, text=True, timeout=15,
    )
    assert result.returncode != 0
    assert "Expected exactly one wheel for eios-kernel" in (result.stdout + result.stderr)
    assert "AttributeError" not in (result.stdout + result.stderr)


def test_both_generated_domain_programs_use_real_binding_names():
    """Guard against unresolved placeholder names in nested adversarial tests."""
    from tools.verify_f5_8_governance_two_domains import _program
    for domain, name in (("sales", "entries"), ("procurement", "bindings")):
        source = _program(domain)
        assert "bindings=existing" not in source
        assert "bindings=" + name in source
        assert source.count("bind_governed_plan(") >= 2
        assert "GOVERNED_CONFIGURATION_CHANGED_DURING_EXECUTION" in source
