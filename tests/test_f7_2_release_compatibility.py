"""F7.2 — exact release compatibility matrix regression tests."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from tools.verify_f7_2_release_compatibility import (
    MATRIX,
    ReleaseCompatibilityError,
    classify_versions,
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


def load_matrix(root: Path) -> dict:
    return json.loads(
        (root / MATRIX.relative_to(ROOT)).read_text(encoding="utf-8")
    )


def test_current_release_tuple_is_exactly_certified():
    result = verify(ROOT)
    assert result["verification"] == "F7_2_RELEASE_COMPATIBILITY_MATRIX_PASS"
    assert result["certified_stack"] == {
        "eios-kernel": "0.1.0",
        "eios-input-contracts": "0.1.0",
        "eios-capability-catalog": "0.1.0",
        "eios-catalog-governance": "0.1.0",
    }
    assert result["default_policy"] == "REJECT_UNLISTED"
    assert result["semver_implies_compatibility"] is False
    assert result["mixed_release_inference"] is False


def test_unlisted_full_stack_is_rejected():
    matrix = load_matrix(ROOT)
    assert classify_versions(
        {
            "eios-kernel": "0.2.0",
            "eios-input-contracts": "0.2.0",
            "eios-capability-catalog": "0.2.0",
            "eios-catalog-governance": "0.2.0",
        },
        matrix=matrix,
    ) == "REJECT_UNLISTED"


def test_mixed_release_is_rejected():
    matrix = load_matrix(ROOT)
    assert classify_versions(
        {
            "eios-kernel": "0.2.0",
            "eios-input-contracts": "0.1.0",
            "eios-capability-catalog": "0.1.0",
            "eios-catalog-governance": "0.1.0",
        },
        matrix=matrix,
    ) == "REJECT_UNLISTED"


def test_partial_tuple_cannot_be_inferred():
    matrix = load_matrix(ROOT)
    with pytest.raises(ReleaseCompatibilityError, match="EXACT_VERSION_TUPLE_REQUIRED"):
        classify_versions(
            {
                "eios-kernel": "0.1.0",
                "eios-input-contracts": "0.1.0",
            },
            matrix=matrix,
        )


def test_bumping_one_package_without_new_matrix_evidence_blocks_ci(tmp_path):
    repo = copy_repo(tmp_path)
    pyproject = repo / "packaging" / "eios-kernel" / "pyproject.toml"
    pyproject.write_text(
        pyproject.read_text(encoding="utf-8").replace(
            'version = "0.1.0"', 'version = "0.2.0"', 1
        ),
        encoding="utf-8",
    )
    with pytest.raises(
        ReleaseCompatibilityError,
        match="CERTIFIED_TUPLE_DOES_NOT_MATCH_DECLARED_PACKAGES",
    ):
        verify(repo)


def test_semver_minor_does_not_auto_admit_candidate(tmp_path):
    repo = copy_repo(tmp_path)
    matrix_path = repo / MATRIX.relative_to(ROOT)
    data = json.loads(matrix_path.read_text(encoding="utf-8"))
    data["certified_combinations"][0]["versions"]["eios-kernel"] = "0.1.1"
    matrix_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ReleaseCompatibilityError):
        verify(repo)


def test_authority_escalation_in_matrix_is_rejected(tmp_path):
    repo = copy_repo(tmp_path)
    matrix_path = repo / MATRIX.relative_to(ROOT)
    data = json.loads(matrix_path.read_text(encoding="utf-8"))
    data["certified_combinations"][0]["production_authorized"] = True
    matrix_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ReleaseCompatibilityError, match="AUTHORITY_ESCALATION"):
        verify(repo)
