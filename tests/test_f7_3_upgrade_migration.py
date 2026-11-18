"""F7.3 — upgrade and migration contract adversarial tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.verify_f7_3_upgrade_migration import (
    CONTRACT,
    MATRIX,
    UpgradeMigrationError,
    validate_migration_request,
    verify,
)

ROOT = Path(__file__).resolve().parents[1]


def load(name: Path) -> dict:
    return json.loads((ROOT / name.relative_to(ROOT)).read_text(encoding="utf-8"))


def base_request():
    contract = load(CONTRACT)
    matrix = load(MATRIX)
    artifacts = set(contract["required_artifacts_before_switch"])
    return contract, matrix, artifacts


def test_contract_verifies_current_baseline():
    result = verify(ROOT)
    assert result["verification"] == "F7_3_UPGRADE_MIGRATION_CONTRACT_PASS"
    assert result["in_place_upgrade_forbidden"] is True
    assert result["switch_before_certification_forbidden"] is True
    assert result["rollback_anchor_required"] is True
    assert result["production_authorized"] is False
    assert result["decision_authority"] is False
    assert result["operational_path"] == "FORBIDDEN"


def test_in_place_upgrade_is_rejected():
    contract, matrix, artifacts = base_request()
    with pytest.raises(UpgradeMigrationError, match="IN_PLACE_UPGRADE_FORBIDDEN"):
        validate_migration_request(
            source_versions=contract["source_stack"],
            candidate_versions=contract["source_stack"],
            source_environment="env/current",
            candidate_environment="env/current",
            rollback_anchor="env/current",
            candidate_certified=True,
            source_environment_mutated=False,
            switch_requested=True,
            required_artifacts_present=artifacts,
            contract=contract,
            matrix=matrix,
        )


def test_unverified_candidate_release_is_rejected():
    contract, matrix, artifacts = base_request()
    candidate = dict(contract["source_stack"])
    candidate["eios-kernel"] = "0.2.0"
    with pytest.raises(UpgradeMigrationError, match="CANDIDATE_NOT_F7_2_CERTIFIED"):
        validate_migration_request(
            source_versions=contract["source_stack"],
            candidate_versions=candidate,
            source_environment="env/source",
            candidate_environment="env/candidate",
            rollback_anchor="env/source",
            candidate_certified=True,
            source_environment_mutated=False,
            switch_requested=True,
            required_artifacts_present=artifacts,
            contract=contract,
            matrix=matrix,
        )


def test_switch_before_all_evidence_is_rejected():
    contract, matrix, artifacts = base_request()
    artifacts.remove("WINDOWS_PYTHON_3_12_CERTIFICATION_RECEIPT")
    with pytest.raises(UpgradeMigrationError, match="SWITCH_BLOCKED_MISSING_ARTIFACTS"):
        validate_migration_request(
            source_versions=contract["source_stack"],
            candidate_versions=contract["source_stack"],
            source_environment="env/source",
            candidate_environment="env/candidate",
            rollback_anchor="env/source",
            candidate_certified=True,
            source_environment_mutated=False,
            switch_requested=True,
            required_artifacts_present=artifacts,
            contract=contract,
            matrix=matrix,
        )


def test_missing_rollback_anchor_is_rejected():
    contract, matrix, artifacts = base_request()
    with pytest.raises(UpgradeMigrationError, match="ROLLBACK_ANCHOR_REQUIRED"):
        validate_migration_request(
            source_versions=contract["source_stack"],
            candidate_versions=contract["source_stack"],
            source_environment="env/source",
            candidate_environment="env/candidate",
            rollback_anchor=None,
            candidate_certified=True,
            source_environment_mutated=False,
            switch_requested=True,
            required_artifacts_present=artifacts,
            contract=contract,
            matrix=matrix,
        )


def test_source_mutation_is_rejected():
    contract, matrix, artifacts = base_request()
    with pytest.raises(
        UpgradeMigrationError,
        match="SOURCE_ENVIRONMENT_MUST_REMAIN_UNMODIFIED",
    ):
        validate_migration_request(
            source_versions=contract["source_stack"],
            candidate_versions=contract["source_stack"],
            source_environment="env/source",
            candidate_environment="env/candidate",
            rollback_anchor="env/source",
            candidate_certified=True,
            source_environment_mutated=True,
            switch_requested=False,
            required_artifacts_present=artifacts,
            contract=contract,
            matrix=matrix,
        )


def test_certified_parallel_candidate_can_reach_switch_eligible():
    contract, matrix, artifacts = base_request()
    result = validate_migration_request(
        source_versions=contract["source_stack"],
        candidate_versions=contract["source_stack"],
        source_environment="env/source",
        candidate_environment="env/candidate",
        rollback_anchor="env/source",
        candidate_certified=True,
        source_environment_mutated=False,
        switch_requested=True,
        required_artifacts_present=artifacts,
        contract=contract,
        matrix=matrix,
    )
    assert result["status"] == "MIGRATION_SWITCH_ELIGIBLE"
    assert result["source_environment_unmodified"] is True
    assert result["candidate_f7_2_status"] == "CERTIFIED"
