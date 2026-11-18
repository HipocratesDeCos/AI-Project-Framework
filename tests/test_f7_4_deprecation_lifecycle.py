"""F7.4 — deprecation and support lifecycle adversarial tests."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from tools.verify_f7_4_deprecation_lifecycle import (
    BASELINE,
    POLICY,
    DeprecationLifecycleError,
    evaluate_deprecation_record,
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


def load(root: Path, path: Path) -> dict:
    return json.loads((root / path.relative_to(ROOT)).read_text(encoding="utf-8"))


def valid_record(root: Path) -> dict:
    baseline = load(root, BASELINE)
    package = baseline["packages"][0]
    return {
        "distribution": package["distribution"],
        "module": package["module"],
        "symbol": package["exports"][0],
        "deprecated_in_release": "0.2.0",
        "status": "DEPRECATED",
        "replacement": "eios.kernel.execution.NewKernelCapabilityResult",
        "rationale": "",
        "migration_guide": "08_Implementacion/example_migration.md",
        "certified_successor_releases": [],
        "compatibility_evidence": [],
        "consumer_regression_evidence": [],
        "third_domain_regression_evidence": [],
        "migration_contract_evidence": [],
    }


def test_current_public_api_remains_active_and_policy_passes():
    result = verify(ROOT)
    assert result["verification"] == "F7_4_DEPRECATION_SUPPORT_LIFECYCLE_PASS"
    assert result["active_public_api"] is True
    assert result["deprecation_record_count"] == 0
    assert result["silent_removal_forbidden"] is True
    assert result["certified_successor_required_before_removal"] is True


def test_public_symbol_can_enter_deprecated_state_without_being_removed():
    baseline = load(ROOT, BASELINE)
    policy = load(ROOT, POLICY)
    record = valid_record(ROOT)
    assert evaluate_deprecation_record(
        record,
        baseline=baseline,
        required_fields=policy["required_deprecation_record_fields"],
    ) == "DEPRECATED"


def test_non_public_symbol_cannot_be_deprecated_as_public_api():
    baseline = load(ROOT, BASELINE)
    policy = load(ROOT, POLICY)
    record = valid_record(ROOT)
    record["symbol"] = "_private_helper"
    with pytest.raises(
        DeprecationLifecycleError,
        match="NON_PUBLIC_SYMBOL_CANNOT_ENTER_LIFECYCLE",
    ):
        evaluate_deprecation_record(
            record,
            baseline=baseline,
            required_fields=policy["required_deprecation_record_fields"],
        )


def test_removal_eligible_requires_certified_successor_release():
    baseline = load(ROOT, BASELINE)
    policy = load(ROOT, POLICY)
    record = valid_record(ROOT)
    record["status"] = "REMOVAL_ELIGIBLE"
    with pytest.raises(
        DeprecationLifecycleError,
        match="CERTIFIED_SUCCESSOR_RELEASE_REQUIRED",
    ):
        evaluate_deprecation_record(
            record,
            baseline=baseline,
            required_fields=policy["required_deprecation_record_fields"],
        )


def test_removal_eligible_requires_all_transition_evidence():
    baseline = load(ROOT, BASELINE)
    policy = load(ROOT, POLICY)
    record = valid_record(ROOT)
    record["status"] = "REMOVAL_ELIGIBLE"
    record["certified_successor_releases"] = ["NEUTRAL_STACK_0_2_0"]
    with pytest.raises(
        DeprecationLifecycleError,
        match="REMOVAL_EVIDENCE_REQUIRED",
    ):
        evaluate_deprecation_record(
            record,
            baseline=baseline,
            required_fields=policy["required_deprecation_record_fields"],
        )


def test_replacement_or_rationale_is_mandatory():
    baseline = load(ROOT, BASELINE)
    policy = load(ROOT, POLICY)
    record = valid_record(ROOT)
    record["replacement"] = ""
    record["rationale"] = ""
    with pytest.raises(
        DeprecationLifecycleError,
        match="REPLACEMENT_OR_RATIONALE_REQUIRED",
    ):
        evaluate_deprecation_record(
            record,
            baseline=baseline,
            required_fields=policy["required_deprecation_record_fields"],
        )


def test_migration_guide_is_mandatory():
    baseline = load(ROOT, BASELINE)
    policy = load(ROOT, POLICY)
    record = valid_record(ROOT)
    record["migration_guide"] = ""
    with pytest.raises(
        DeprecationLifecycleError,
        match="MIGRATION_GUIDE_REQUIRED",
    ):
        evaluate_deprecation_record(
            record,
            baseline=baseline,
            required_fields=policy["required_deprecation_record_fields"],
        )


def test_current_baseline_forbids_pre_authorized_removed_state(tmp_path):
    repo = copy_repo(tmp_path)
    policy_path = repo / POLICY.relative_to(ROOT)
    data = json.loads(policy_path.read_text(encoding="utf-8"))
    record = valid_record(repo)
    record["status"] = "REMOVED"
    record["certified_successor_releases"] = ["NEUTRAL_STACK_0_2_0"]
    record["compatibility_evidence"] = ["F7.2"]
    record["consumer_regression_evidence"] = ["consumer-regression"]
    record["third_domain_regression_evidence"] = ["third-domain"]
    record["migration_contract_evidence"] = ["F7.3"]
    data["deprecations"] = [record]
    policy_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(
        DeprecationLifecycleError,
        match="NO_PUBLIC_API_REMOVAL_AUTHORIZED_IN_F7_4_BASELINE",
    ):
        verify(repo)
