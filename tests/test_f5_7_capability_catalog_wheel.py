"""F5.7: optional catalog wheel is isolated, canonical and pinned."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tomllib
import zipfile

import pytest

from tools.build_eios_capability_catalog_distribution import (
    ALLOWED_INTERNAL_IMPORTS, METADATA_FILE, REQUIRED_DEPENDENCIES,
    ROOT, SOURCE_FILES, audit_wheel, stage_distribution, verify_source_dependencies,
)
from tools.build_eios_input_contracts_distribution import SOURCE_FILES as INPUT_FILES
from tools.build_eios_kernel_distribution import SOURCE_FILES as KERNEL_FILES
from tools.build_eios_price_distribution import SOURCE_FILES as PRICE_FILES
from tools.build_eios_tco_distribution import SOURCE_FILES as TCO_FILES
from tools.build_eios_contracts_distribution import SOURCE_FILES as C0_FILES

EXPECTED = {
    Path("eios/capability_catalog/__init__.py"),
    Path("eios/capability_catalog/catalog.py"),
}


def test_manifest_is_dedicated_to_catalog_and_uses_exact_neutral_api_pins():
    assert set(SOURCE_FILES) == EXPECTED
    assert ALLOWED_INTERNAL_IMPORTS == {
        "eios.capability_catalog.catalog",
        "eios.kernel.execution",
        "eios.input_contracts",
    }
    assert REQUIRED_DEPENDENCIES == {
        "pydantic": None,
        "eios-kernel": "0.1.0",
        "eios-input-contracts": "0.1.0",
    }
    for other in (INPUT_FILES, KERNEL_FILES, PRICE_FILES, TCO_FILES, C0_FILES):
        assert EXPECTED.isdisjoint(other)
    verify_source_dependencies(ROOT)
    meta = tomllib.loads((ROOT / METADATA_FILE).read_text(encoding="utf-8"))
    assert meta["project"]["name"] == "eios-capability-catalog"
    assert meta["project"]["version"] == "0.1.0"
    assert meta["project"]["dependencies"] == [
        "pydantic>=2.0,<3.0", "eios-kernel==0.1.0",
        "eios-input-contracts==0.1.0",
    ]


def test_stage_is_byte_identical_and_contains_no_business_modules(tmp_path):
    stage_distribution(tmp_path)
    stage = tmp_path / "src"
    copied = {p.relative_to(stage) for p in stage.rglob("*.py")}
    assert copied == EXPECTED
    for path in EXPECTED:
        assert (stage / path).read_bytes() == (ROOT / path).read_bytes()
    assert not (stage / "eios/core/models.py").exists()
    assert not (stage / "eios/input_contracts/contracts.py").exists()
    assert not (stage / "eios/kernel/execution.py").exists()


@pytest.mark.parametrize("illegal", (
    "from eios.core.models import PurchaseOperation",
    "from eios.pricing.engine import run_price_intelligence",
    "from eios.tco.engine import calculate_tco",
    "from eios.company_app import main",
    "from ..core.models import PurchaseOperation",
    "from .some_unbundled_module import foo",
))
def test_new_internal_business_dependency_fails_closed(tmp_path, illegal):
    for path in EXPECTED:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())
    source = tmp_path / "eios/capability_catalog/catalog.py"
    source.write_text(source.read_text(encoding="utf-8") + "\n" + illegal + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Forbidden"):
        verify_source_dependencies(tmp_path)


def make_wheel(wheel, *, extra=(), requirements=(
    "Requires-Dist: pydantic>=2,<3",
    "Requires-Dist: eios-kernel==0.1.0",
    "Requires-Dist: eios-input-contracts==0.1.0",
)):
    with zipfile.ZipFile(wheel, "w") as archive:
        for path in EXPECTED:
            archive.writestr(path.as_posix(), "# synthetic approved module\n")
        for additional in extra:
            archive.writestr(additional, "# unwanted payload\n")
        archive.writestr(
            "eios_capability_catalog-0.1.0.dist-info/METADATA",
            "Metadata-Version: 2.3\nName: eios-capability-catalog\n"
            "Version: 0.1.0\n" + "\n".join(requirements) + "\n",
        )


def test_wheel_accepts_closed_set_and_explicit_version_pins(tmp_path):
    wheel = tmp_path / "catalog.whl"
    make_wheel(wheel)
    audit_wheel(wheel)


@pytest.mark.parametrize("extra", (
    "eios/kernel/execution.py",
    "eios/input_contracts/contracts.py",
    "eios/capability_catalog/unexpected.py",
    "eios/core/models.py",
    "eios/capability_catalog/__pycache__/catalog.pyc",
))
def test_wheel_rejects_physical_collisions_and_unapproved_paths(tmp_path, extra):
    wheel = tmp_path / "catalog.whl"
    make_wheel(wheel, extra=(extra,))
    with pytest.raises(ValueError, match="Unexpected|Unapproved"):
        audit_wheel(wheel)


@pytest.mark.parametrize("deps,expected", (
    (("Requires-Dist: pydantic>=2,<3",), "only"),
    (("Requires-Dist: pydantic>=2,<3", "Requires-Dist: eios-kernel>=0.1.0", "Requires-Dist: eios-input-contracts==0.1.0"), "Exact"),
    (("Requires-Dist: pydantic>=2,<3", "Requires-Dist: eios-kernel==0.1.0", "Requires-Dist: eios-input-contracts>=0.1.0"), "Exact"),
    (("Requires-Dist: pydantic>=2,<3", "Requires-Dist: eios-kernel==0.1.0", "Requires-Dist: eios-input-contracts==0.1.0", "Requires-Dist: openpyxl>=3"), "only"),
))
def test_wheel_rejects_missing_unpinned_and_business_deps(tmp_path, deps, expected):
    wheel = tmp_path / "catalog.whl"
    make_wheel(wheel, requirements=deps)
    with pytest.raises(ValueError, match="Exact|only"):
        audit_wheel(wheel)


def test_bundled_extra_import_rejected_even_with_correct_file_set(tmp_path):
    wheel = tmp_path / "catalog.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("eios/capability_catalog/__init__.py", "# synthetic\n")
        archive.writestr("eios/capability_catalog/catalog.py", "import eios.pricing.engine\n")
        archive.writestr(
            "eios_capability_catalog-0.1.0.dist-info/METADATA",
            "Name: eios-capability-catalog\nVersion: 0.1.0\n"
            "Requires-Dist: pydantic>=2,<3\n"
            "Requires-Dist: eios-kernel==0.1.0\n"
            "Requires-Dist: eios-input-contracts==0.1.0\n",
        )
    with pytest.raises(ValueError, match="Forbidden"):
        audit_wheel(wheel)


def test_cli_verifier_resolves_real_dir_args_before_installation(tmp_path):
    runner = ROOT / "tools/verify_f5_7_capability_catalog.py"
    if not runner.is_file():
        pytest.fail("F5.7 real two-domain verifier is missing")
    process = subprocess.run(
        [sys.executable, str(runner),
         "--kernel-dir", str(tmp_path), "--inputs-dir", str(tmp_path),
         "--catalog-dir", str(tmp_path), "--contracts-dir", str(tmp_path),
         "--price-dir", str(tmp_path), "--tco-dir", str(tmp_path)],
        cwd=tmp_path, capture_output=True, text=True, timeout=15,
    )
    assert process.returncode != 0
    assert "Expected exactly one wheel for eios-kernel" in process.stdout + process.stderr
    assert "AttributeError" not in process.stdout + process.stderr
