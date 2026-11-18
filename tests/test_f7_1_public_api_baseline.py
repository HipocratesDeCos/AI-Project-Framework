"""F7.1 — public API baseline and accidental breaking-change guards."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from tools.verify_f7_1_public_api_baseline import (
    PublicApiBaselineError,
    verify,
)

ROOT = Path(__file__).resolve().parents[1]


def copy_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "dist"),
    )
    return target


def manifest_path(root: Path) -> Path:
    return root / "08_Implementacion" / "phase7_public_api_baseline_v0.1.json"


def mutate_manifest(root: Path, mutate) -> None:
    path = manifest_path(root)
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def test_current_public_api_matches_baseline():
    result = verify(ROOT)
    assert result["verification"] == "F7_1_PUBLIC_API_BASELINE_PASS"
    assert result["neutral_distributions"] == [
        "eios-kernel",
        "eios-input-contracts",
        "eios-capability-catalog",
        "eios-catalog-governance",
    ]
    assert result["breaking_change_requires_new_evidence"] is True
    assert result["semver_implies_compatibility"] is False
    assert result["production_authorized"] is False
    assert result["decision_authority"] is False
    assert result["operational_path"] == "FORBIDDEN"


def test_removed_public_export_is_detected(tmp_path):
    repo = copy_repo(tmp_path)
    mutate_manifest(
        repo,
        lambda data: data["packages"][1]["exports"].remove("CapabilityInputBinding"),
    )
    with pytest.raises(PublicApiBaselineError, match="EXPORT_SET_OR_ORDER_CHANGED"):
        verify(repo)


def test_function_signature_drift_is_detected(tmp_path):
    repo = copy_repo(tmp_path)
    mutate_manifest(
        repo,
        lambda data: data["packages"][0]["functions"]["execute_kernel"].append(
            ["new_required_argument", "POSITIONAL_OR_KEYWORD", False]
        ),
    )
    with pytest.raises(PublicApiBaselineError, match="FUNCTION_SIGNATURE_CHANGED"):
        verify(repo)


def test_model_field_drift_is_detected(tmp_path):
    repo = copy_repo(tmp_path)
    mutate_manifest(
        repo,
        lambda data: data["packages"][0]["pydantic_models"]["KernelContext"].append(
            "new_field"
        ),
    )
    with pytest.raises(PublicApiBaselineError, match="PYDANTIC_FIELDS_CHANGED"):
        verify(repo)


def test_distribution_version_drift_is_detected(tmp_path):
    repo = copy_repo(tmp_path)
    pyproject = repo / "packaging" / "eios-kernel" / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8").replace(
        'version = "0.1.0"', 'version = "0.2.0"', 1,
    )
    pyproject.write_text(text, encoding="utf-8")
    with pytest.raises(PublicApiBaselineError, match="DISTRIBUTION_VERSION_CHANGED"):
        verify(repo)


def test_public_constant_drift_is_detected(tmp_path):
    repo = copy_repo(tmp_path)
    mutate_manifest(
        repo,
        lambda data: data["packages"][2]["constants"].update(
            {"KERNEL_API_VERSION": "9.9.9"}
        ),
    )
    with pytest.raises(PublicApiBaselineError, match="PUBLIC_CONSTANT_CHANGED"):
        verify(repo)


def test_business_specific_modules_are_not_promoted_to_public_motor_api(tmp_path):
    repo = copy_repo(tmp_path)
    mutate_manifest(
        repo,
        lambda data: data["excluded_from_public_baseline"].remove("eios.pricing"),
    )
    with pytest.raises(PublicApiBaselineError, match="BUSINESS_MODULE_EXCLUSION_MISSING"):
        verify(repo)
