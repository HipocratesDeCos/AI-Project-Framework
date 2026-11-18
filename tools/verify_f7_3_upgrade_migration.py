"""F7.3 — verify upgrade/migration contract invariants for the neutral EIOS Motor."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.verify_f7_2_release_compatibility import classify_versions

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "08_Implementacion" / "phase7_upgrade_migration_contract_v0.1.json"
MATRIX = ROOT / "08_Implementacion" / "phase7_release_compatibility_matrix_v0.1.json"


class UpgradeMigrationError(ValueError):
    pass


def fail(code: str) -> None:
    raise UpgradeMigrationError("F7_3_UPGRADE_MIGRATION_REJECTED:" + code)


def _load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        fail("INVALID_JSON:" + str(exc))
    if type(data) is not dict:
        fail("OBJECT_REQUIRED")
    return data


def validate_migration_request(
    *,
    source_versions: dict[str, str],
    candidate_versions: dict[str, str],
    source_environment: str,
    candidate_environment: str,
    rollback_anchor: str | None,
    candidate_certified: bool,
    source_environment_mutated: bool,
    switch_requested: bool,
    required_artifacts_present: set[str],
    contract: dict[str, Any],
    matrix: dict[str, Any],
) -> dict[str, Any]:
    if source_environment == candidate_environment:
        fail("IN_PLACE_UPGRADE_FORBIDDEN")
    if source_environment_mutated:
        fail("SOURCE_ENVIRONMENT_MUST_REMAIN_UNMODIFIED")
    if source_versions != contract["source_stack"]:
        fail("SOURCE_STACK_NOT_BASELINE")
    if rollback_anchor is None or not rollback_anchor.strip():
        fail("ROLLBACK_ANCHOR_REQUIRED")

    candidate_status = classify_versions(candidate_versions, matrix=matrix)
    if candidate_status != "CERTIFIED":
        fail("CANDIDATE_NOT_F7_2_CERTIFIED")
    if not candidate_certified:
        fail("CANDIDATE_CERTIFICATION_RECEIPT_REQUIRED")

    required = set(contract["required_artifacts_before_switch"])
    missing = required - required_artifacts_present
    if switch_requested and missing:
        fail("SWITCH_BLOCKED_MISSING_ARTIFACTS:" + ",".join(sorted(missing)))

    return {
        "status": "MIGRATION_SWITCH_ELIGIBLE" if switch_requested else "MIGRATION_PRECHECK_PASS",
        "source_environment": source_environment,
        "candidate_environment": candidate_environment,
        "source_stack": source_versions,
        "candidate_stack": candidate_versions,
        "rollback_anchor": rollback_anchor,
        "source_environment_unmodified": True,
        "candidate_f7_2_status": candidate_status,
        "production_authorized": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }


def verify(root: Path = ROOT) -> dict[str, Any]:
    contract = _load(root / CONTRACT.relative_to(ROOT))
    matrix = _load(root / MATRIX.relative_to(ROOT))

    expected_top = {
        "schema", "phase", "baseline_main_sha", "policy", "source_stack",
        "candidate_stack_policy", "states", "allowed_transitions",
        "failure_transitions", "required_artifacts_before_switch",
        "rollback_requirements",
    }
    if set(contract) != expected_top:
        fail("CONTRACT_SCHEMA_CHANGED")
    if contract["schema"] != "EIOS_UPGRADE_MIGRATION_CONTRACT/v0.1":
        fail("CONTRACT_IDENTITY_CHANGED")
    if contract["phase"] != "F7.3":
        fail("PHASE_CHANGED")
    if contract["baseline_main_sha"] != "de7d8c046fb58f2727bf0c40a405c22a3a6621d7":
        fail("BASELINE_MAIN_SHA_CHANGED")

    expected_policy = {
        "in_place_upgrade_forbidden": True,
        "mixed_release_runtime_forbidden": True,
        "candidate_environment_must_be_new": True,
        "switch_before_certification_forbidden": True,
        "rollback_anchor_required": True,
        "partial_migration_is_failure": True,
        "production_authorized": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }
    if contract["policy"] != expected_policy:
        fail("MIGRATION_POLICY_CHANGED")

    if classify_versions(contract["source_stack"], matrix=matrix) != "CERTIFIED":
        fail("SOURCE_STACK_NOT_F7_2_CERTIFIED")

    expected_states = [
        "SOURCE_ACTIVE",
        "CANDIDATE_PREPARED",
        "CANDIDATE_CERTIFIED",
        "SWITCH_COMMITTED",
        "ROLLBACK_COMMITTED",
        "MIGRATION_REJECTED",
    ]
    if contract["states"] != expected_states:
        fail("STATE_MACHINE_CHANGED")

    allowed = {
        ("SOURCE_ACTIVE", "CANDIDATE_PREPARED"),
        ("CANDIDATE_PREPARED", "CANDIDATE_CERTIFIED"),
        ("CANDIDATE_CERTIFIED", "SWITCH_COMMITTED"),
        ("SWITCH_COMMITTED", "ROLLBACK_COMMITTED"),
    }
    if {tuple(x) for x in contract["allowed_transitions"]} != allowed:
        fail("ALLOWED_TRANSITIONS_CHANGED")

    forbidden_direct = {
        ("SOURCE_ACTIVE", "SWITCH_COMMITTED"),
        ("CANDIDATE_PREPARED", "SWITCH_COMMITTED"),
        ("SOURCE_ACTIVE", "ROLLBACK_COMMITTED"),
    }
    if forbidden_direct & {tuple(x) for x in contract["allowed_transitions"]}:
        fail("UNSAFE_DIRECT_TRANSITION_ENABLED")

    required_artifacts = {
        "SOURCE_STACK_FINGERPRINT",
        "SOURCE_CERTIFICATION_RECEIPT",
        "CANDIDATE_STACK_FINGERPRINT",
        "CANDIDATE_F7_2_CERTIFICATION",
        "CANDIDATE_FRESH_INSTALL_RECEIPT",
        "EXISTING_CONSUMER_REGRESSION_RECEIPT",
        "THIRD_DOMAIN_REGRESSION_RECEIPT",
        "LINUX_CERTIFICATION_RECEIPT",
        "WINDOWS_PYTHON_3_12_CERTIFICATION_RECEIPT",
        "ROLLBACK_ANCHOR",
    }
    if set(contract["required_artifacts_before_switch"]) != required_artifacts:
        fail("SWITCH_EVIDENCE_SET_CHANGED")

    rollback = {
        "SOURCE_ENVIRONMENT_UNMODIFIED",
        "SOURCE_STACK_FINGERPRINT_MATCH",
        "SOURCE_CERTIFICATION_RECEIPT_MATCH",
        "NO_DATA_OR_SCHEMA_DESTRUCTIVE_STEP_WITHOUT_SEPARATE_MIGRATION_EVIDENCE",
    }
    if set(contract["rollback_requirements"]) != rollback:
        fail("ROLLBACK_REQUIREMENTS_CHANGED")

    synthetic_artifacts = set(required_artifacts)
    result = validate_migration_request(
        source_versions=contract["source_stack"],
        candidate_versions=contract["source_stack"],
        source_environment="env/source-0.1.0",
        candidate_environment="env/candidate-0.1.0-revalidated",
        rollback_anchor="env/source-0.1.0",
        candidate_certified=True,
        source_environment_mutated=False,
        switch_requested=True,
        required_artifacts_present=synthetic_artifacts,
        contract=contract,
        matrix=matrix,
    )
    if result["status"] != "MIGRATION_SWITCH_ELIGIBLE":
        fail("REFERENCE_MIGRATION_PRECHECK_FAILED")

    return {
        "verification": "F7_3_UPGRADE_MIGRATION_CONTRACT_PASS",
        "phase": "F7.3",
        "source_stack": contract["source_stack"],
        "in_place_upgrade_forbidden": True,
        "switch_before_certification_forbidden": True,
        "rollback_anchor_required": True,
        "production_authorized": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }


def main() -> None:
    print(json.dumps(verify(), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
