"""F5.9 — audit a fully independent third project and guard portability rules.

The full end-to-end proof runs in GitHub Actions through the separate isolated
venv verifier. These tests catch packaging, import and provenance shortcuts
quickly before the expensive full F4/F5 integration regression.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tomllib
import zipfile

import pytest

from tools.verify_f5_9_third_domain import (
    ALLOWED_EIOS_IMPORTS, FIXTURE_ROOT, NEUTRAL_WHEELS,
    PROJECT_MODULES, PROJECT_NAME, PROJECT_VERSION,
    REQUIRED_DEPENDENCIES, audit_project_source, audit_project_wheel,
    check, _source_files,
)
from tools.verify_f5_8_governance_two_domains import (
    WHEEL_SPECS,
)

META = "eios_maintenance_example-0.1.0.dist-info/METADATA"
EXPECTED_WHEEL_DEPS = (
    "Requires-Dist: pydantic>=2.0,<3.0",
    "Requires-Dist: eios-kernel==0.1.0",
    "Requires-Dist: eios-input-contracts==0.1.0",
    "Requires-Dist: eios-capability-catalog==0.1.0",
    "Requires-Dist: eios-catalog-governance==0.1.0",
)


def _fake_consumer_wheel(target, *, extra=(), deps=EXPECTED_WHEEL_DEPS, mutate=None):
    with zipfile.ZipFile(target, "w") as archive:
        for name, file in _source_files().items():
            data = file.read_bytes()
            if name == mutate:
                data += b"\n# malicious mutation in packaged source\n"
            archive.writestr(name, data)
        for addition in extra:
            archive.writestr(addition, "# unauthorized consumer payload\n")
        archive.writestr(
            META, "Metadata-Version: 2.3\nName: eios-maintenance-example\n"
                  "Version: 0.1.0\n" + "\n".join(deps) + "\n",
        )


def test_third_project_is_a_separate_named_distribution_not_an_eios_module():
    manifest = tomllib.loads(
        (FIXTURE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    assert manifest["project"]["name"] == PROJECT_NAME
    assert manifest["project"]["version"] == PROJECT_VERSION
    assert len(PROJECT_MODULES) == 2
    assert all(name.startswith("eios_maintenance_example/") for name in PROJECT_MODULES)
    assert set(REQUIRED_DEPENDENCIES) == {
        "pydantic", "eios-kernel", "eios-input-contracts",
        "eios-capability-catalog", "eios-catalog-governance",
    }
    assert NEUTRAL_WHEELS == (
        "eios-kernel", "eios-input-contracts",
        "eios-capability-catalog", "eios-catalog-governance",
    )
    assert set(NEUTRAL_WHEELS) < set(WHEEL_SPECS)
    assert "eios.pricing" not in ALLOWED_EIOS_IMPORTS
    assert "eios.core.models" not in ALLOWED_EIOS_IMPORTS
    audit_project_source()


@pytest.mark.parametrize("forbidden", (
    "import eios.pricing.engine",
    "from eios.core.models import PurchaseOperation",
    "from eios.tco.engine import calculate_tco",
    "from eios.company_app import main",
    "from .another_module import read_ledger",
))
def test_business_imports_or_unbundled_relative_import_are_rejected(tmp_path, forbidden):
    source = tmp_path / "copied"
    shutil.copytree(FIXTURE_ROOT, source)
    file = source / "src/eios_maintenance_example/consumer.py"
    file.write_text(file.read_text(encoding="utf-8") + "\n" + forbidden + "\n")
    with pytest.raises(ValueError, match="import|domain|business|absolute"):
        audit_project_source(source)


def test_wheel_audit_accepts_identical_third_party_modules_and_locked_dependencies(tmp_path):
    wheel = tmp_path / "consumer.whl"
    _fake_consumer_wheel(wheel)
    from hashlib import sha256
    assert audit_project_wheel(wheel) == {
        name: sha256(path.read_bytes()).hexdigest()
        for name, path in _source_files().items()
    }


@pytest.mark.parametrize("extra", (
    "eios/core/models.py",
    "eios/pricing/engine.py",
    "eios/tco/engine.py",
    "eios/input_contracts/contracts.py",
    "eios_maintenance_example/hidden_secret.json",
    "eios_maintenance_example/other.py",
))
def test_wheel_refuses_bundled_engine_code_or_hidden_consumer_files(tmp_path, extra):
    wheel = tmp_path / "consumer.whl"
    _fake_consumer_wheel(wheel, extra=(extra,))
    with pytest.raises(ValueError, match="illegally|differ"):
        audit_project_wheel(wheel)


def test_wrong_consumer_code_bytes_are_refused_before_pip_install(tmp_path):
    wheel = tmp_path / "consumer.whl"
    _fake_consumer_wheel(
        wheel, mutate="eios_maintenance_example/consumer.py",
    )
    with pytest.raises(ValueError, match="differs from canonical"):
        audit_project_wheel(wheel)


@pytest.mark.parametrize("dependencies", (
    EXPECTED_WHEEL_DEPS[:-1],
    EXPECTED_WHEEL_DEPS + ("Requires-Dist: eios-price-procurement==0.2.0",),
    tuple(
        dep.replace("eios-kernel==0.1.0", "eios-kernel>=0.1.0")
        for dep in EXPECTED_WHEEL_DEPS
    ),
    tuple(
        dep.replace("eios-catalog-governance==0.1.0", "eios-catalog-governance>=0.1.0")
        for dep in EXPECTED_WHEEL_DEPS
    ),
))
def test_deps_must_pin_exactly_four_neutral_eios_distributions(tmp_path, dependencies):
    wheel = tmp_path / "consumer.whl"
    _fake_consumer_wheel(wheel, deps=dependencies)
    with pytest.raises(ValueError, match="dependency"):
        audit_project_wheel(wheel)


def test_audit_rejects_accidental_extra_business_module_in_source_tree(tmp_path):
    source = tmp_path / "copied"
    shutil.copytree(FIXTURE_ROOT, source)
    extra = source / "src/eios_maintenance_example/purchase_adapter.py"
    extra.write_text("from eios.core.models import PurchaseOperation\n")
    with pytest.raises(ValueError, match="unexpected modules"):
        audit_project_source(source)


def test_verifier_cli_fails_before_installing_if_wheel_missing(tmp_path):
    runner = Path(__file__).resolve().parents[1] / "tools/verify_f5_9_third_domain.py"
    cmd = [sys.executable, str(runner)]
    for folder in ("kernel", "inputs", "catalog", "governance"):
        cmd.extend([f"--{folder}-dir", str(tmp_path)])
    process = subprocess.run(
        cmd, cwd=tmp_path, capture_output=True, text=True, timeout=15,
    )
    assert process.returncode != 0
    assert "Expected exactly one wheel for eios-kernel" in (
        process.stdout + process.stderr
    )
    assert "AttributeError" not in process.stdout + process.stderr


def test_verifier_refuses_any_extra_domain_wheel():
    with pytest.raises(ValueError, match="exactly the four neutral EIOS wheels"):
        check({name: Path("/nonexistent") for name in NEUTRAL_WHEELS} | {
            "eios-price-procurement": Path("/also-nonexistent"),
        })


def test_maintenance_runtime_source_contains_explicit_documentary_missing_gate():
    source = (FIXTURE_ROOT / "src/eios_maintenance_example/consumer.py").read_text()
    assert "SYNTHETIC_SAFETY_INSPECTION_EVIDENCE_MISSING" in source
    assert "NOT_EVALUABLE" in source
    assert "GOVERNED_CONFIGURATION_CHANGED_DURING_EXECUTION" in source
    assert "INSUFFICIENT_AUTHORIZATION_SCOPE" in source
    assert "UNVERIFIED_ADAPTER_RESPONSIBILITY" in source
    assert "SYNTHETIC_TEST_DOUBLE_ONLY" in source
    assert 'result.operational_path == "FORBIDDEN"' in source
