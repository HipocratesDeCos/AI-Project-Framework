"""F7.4 — deprecation and support lifecycle policy for public neutral APIs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "08_Implementacion" / "phase7_deprecation_support_lifecycle_v0.1.json"
BASELINE = ROOT / "08_Implementacion" / "phase7_public_api_baseline_v0.1.json"


class DeprecationLifecycleError(ValueError):
    pass


def fail(code: str) -> None:
    raise DeprecationLifecycleError("F7_4_DEPRECATION_LIFECYCLE_REJECTED:" + code)


def _load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        fail("INVALID_JSON:" + str(exc))
    if type(data) is not dict:
        fail("OBJECT_REQUIRED")
    return data


def public_symbols(baseline: dict[str, Any]) -> set[tuple[str, str, str]]:
    result: set[tuple[str, str, str]] = set()
    for package in baseline["packages"]:
        distribution = package["distribution"]
        module = package["module"]
        for symbol in package["exports"]:
            result.add((distribution, module, symbol))
    return result


def evaluate_deprecation_record(
    record: dict[str, Any],
    *,
    baseline: dict[str, Any],
    required_fields: list[str],
) -> str:
    if set(record) != set(required_fields):
        fail("DEPRECATION_RECORD_SCHEMA_CHANGED")

    key = (record["distribution"], record["module"], record["symbol"])
    if key not in public_symbols(baseline):
        fail("NON_PUBLIC_SYMBOL_CANNOT_ENTER_LIFECYCLE")

    if record["status"] not in {"DEPRECATED", "REMOVAL_ELIGIBLE", "REMOVED"}:
        fail("INVALID_DEPRECATION_STATUS")

    if type(record["deprecated_in_release"]) is not str or not record["deprecated_in_release"]:
        fail("DEPRECATED_RELEASE_REQUIRED")

    replacement = record["replacement"]
    rationale = record["rationale"]
    if not (
        (type(replacement) is str and replacement.strip())
        or (type(rationale) is str and rationale.strip())
    ):
        fail("REPLACEMENT_OR_RATIONALE_REQUIRED")

    if type(record["migration_guide"]) is not str or not record["migration_guide"].strip():
        fail("MIGRATION_GUIDE_REQUIRED")

    successors = record["certified_successor_releases"]
    if type(successors) is not list:
        fail("CERTIFIED_SUCCESSOR_RELEASES_MUST_BE_LIST")

    evidence_fields = [
        "compatibility_evidence",
        "consumer_regression_evidence",
        "third_domain_regression_evidence",
        "migration_contract_evidence",
    ]
    for field in evidence_fields:
        if type(record[field]) is not list:
            fail("EVIDENCE_MUST_BE_LIST:" + field)

    if record["status"] in {"REMOVAL_ELIGIBLE", "REMOVED"}:
        if len(successors) < 1:
            fail("CERTIFIED_SUCCESSOR_RELEASE_REQUIRED")
        for field in evidence_fields:
            if len(record[field]) < 1:
                fail("REMOVAL_EVIDENCE_REQUIRED:" + field)

    return record["status"]


def verify(root: Path = ROOT) -> dict[str, Any]:
    policy = _load(root / POLICY.relative_to(ROOT))
    baseline = _load(root / BASELINE.relative_to(ROOT))

    expected_top = {
        "schema", "phase", "baseline_main_sha", "policy", "states",
        "allowed_transitions", "current_public_api_status", "deprecations",
        "required_deprecation_record_fields",
        "removal_eligibility_requirements",
    }
    if set(policy) != expected_top:
        fail("POLICY_SCHEMA_CHANGED")
    if policy["schema"] != "EIOS_DEPRECATION_SUPPORT_LIFECYCLE/v0.1":
        fail("POLICY_IDENTITY_CHANGED")
    if policy["phase"] != "F7.4":
        fail("PHASE_CHANGED")
    if policy["baseline_main_sha"] != "afbcf7d9a4d1bf3e9657148b8549ff0b4b172f15":
        fail("BASELINE_MAIN_SHA_CHANGED")

    expected_policy = {
        "silent_public_api_removal_forbidden": True,
        "deprecation_record_required_before_removal": True,
        "at_least_one_certified_successor_release_required": True,
        "replacement_or_explicit_rationale_required": True,
        "migration_guidance_required": True,
        "existing_consumer_regression_required": True,
        "third_domain_regression_required": True,
        "f7_2_compatibility_evidence_required": True,
        "f7_3_migration_contract_required": True,
        "removal_without_successor_evidence_forbidden": True,
        "production_authorized": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }
    if policy["policy"] != expected_policy:
        fail("LIFECYCLE_POLICY_CHANGED")

    if policy["states"] != ["ACTIVE", "DEPRECATED", "REMOVAL_ELIGIBLE", "REMOVED"]:
        fail("LIFECYCLE_STATES_CHANGED")

    allowed = [
        ["ACTIVE", "DEPRECATED"],
        ["DEPRECATED", "REMOVAL_ELIGIBLE"],
        ["REMOVAL_ELIGIBLE", "REMOVED"],
    ]
    if policy["allowed_transitions"] != allowed:
        fail("LIFECYCLE_TRANSITIONS_CHANGED")

    if policy["current_public_api_status"] != "ACTIVE":
        fail("CURRENT_API_MUST_REMAIN_ACTIVE")

    required_fields = [
        "distribution",
        "module",
        "symbol",
        "deprecated_in_release",
        "status",
        "replacement",
        "rationale",
        "migration_guide",
        "certified_successor_releases",
        "compatibility_evidence",
        "consumer_regression_evidence",
        "third_domain_regression_evidence",
        "migration_contract_evidence",
    ]
    if policy["required_deprecation_record_fields"] != required_fields:
        fail("DEPRECATION_RECORD_FIELDS_CHANGED")

    required_eligibility = {
        "SYMBOL_WAS_PUBLIC_IN_F7_1",
        "DEPRECATION_RECORD_EXISTS",
        "STATUS_IS_DEPRECATED",
        "AT_LEAST_ONE_CERTIFIED_SUCCESSOR_RELEASE",
        "REPLACEMENT_OR_RATIONALE_PRESENT",
        "MIGRATION_GUIDE_PRESENT",
        "F7_2_COMPATIBILITY_EVIDENCE",
        "EXISTING_CONSUMER_REGRESSION",
        "THIRD_DOMAIN_REGRESSION",
        "F7_3_MIGRATION_CONTRACT_EVIDENCE",
    }
    if set(policy["removal_eligibility_requirements"]) != required_eligibility:
        fail("REMOVAL_ELIGIBILITY_REQUIREMENTS_CHANGED")

    records = policy["deprecations"]
    if type(records) is not list:
        fail("DEPRECATIONS_MUST_BE_LIST")
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        status = evaluate_deprecation_record(
            record,
            baseline=baseline,
            required_fields=required_fields,
        )
        key = (record["distribution"], record["module"], record["symbol"])
        if key in seen:
            fail("DUPLICATE_DEPRECATION_RECORD")
        seen.add(key)
        if status == "REMOVED":
            fail("NO_PUBLIC_API_REMOVAL_AUTHORIZED_IN_F7_4_BASELINE")

    return {
        "verification": "F7_4_DEPRECATION_SUPPORT_LIFECYCLE_PASS",
        "phase": "F7.4",
        "public_symbol_count": len(public_symbols(baseline)),
        "active_public_api": True,
        "deprecation_record_count": len(records),
        "silent_removal_forbidden": True,
        "certified_successor_required_before_removal": True,
        "migration_guidance_required": True,
        "production_authorized": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }


def main() -> None:
    print(json.dumps(verify(), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
