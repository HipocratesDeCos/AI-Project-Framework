"""F6.8 — recovery requires a stopped chain and complete fresh revalidation."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
for fixture_name in (
    "f6_2_external_company_adapter",
    "f6_3_documentary_boundary_consumer",
    "f6_4_custody_consumer",
    "f6_5_onboarding_consumer",
):
    sys.path.insert(0, str(ROOT / "tests" / "fixtures" / fixture_name / "src"))

from eios_onboarding_example.demo import fixture  # noqa: E402
from eios_onboarding_example.onboarding import (  # noqa: E402
    PinnedOnboarding, fingerprint_provider_snapshot,
    review_with_onboarded_providers,
)
from eios_onboarding_example.pilot import assess_read_only_rehearsal  # noqa: E402
from eios_onboarding_example.pilot_demo import manifest_for  # noqa: E402
from eios_onboarding_example.safe_stop import revalidate_before_rehearsal_reuse  # noqa: E402
from eios_onboarding_example.recovery import (  # noqa: E402
    RecoveryError, recover_after_safe_stop,
)
from eios_onboarding_example.recovery_demo import run  # noqa: E402


def stopped_case(tmp_path):
    folder = tmp_path / "case"
    folder.mkdir()
    prepared, request, pin, registry, endpoints = fixture("EXTERNAL_COMPANY_A", folder)
    technical = review_with_onboarded_providers(
        prepared=prepared, request=request, pin=pin,
        registry_source=registry, endpoints=endpoints,
    )
    manifest = manifest_for(pin, request)
    stale = assess_read_only_rehearsal(
        manifest=manifest, pin=pin, request=request,
        technical_review=technical,
    )
    registry.snapshot = replace(registry.snapshot, revision=2)
    stopped = revalidate_before_rehearsal_reuse(
        previous=stale, manifest=manifest, prepared=prepared,
        request=request, pin=pin, registry_source=registry, endpoints=endpoints,
    )
    assert stopped.status == "SAFE_STOPPED"
    return [prepared, request, pin, registry, endpoints, manifest, stale, stopped]


def recovered_inputs(items):
    restored = items[3].snapshot
    fresh_pin = PinnedOnboarding(
        project_id=restored.project_id,
        company_id=restored.company_id,
        expected_revision=restored.revision,
        expected_digest=fingerprint_provider_snapshot(restored),
    )
    fresh_manifest = manifest_for(fresh_pin, items[1])
    return fresh_pin, fresh_manifest


def recover(items, pin, manifest):
    return recover_after_safe_stop(
        stopped=items[7], stale=items[6], manifest=manifest,
        prepared=items[0], request=items[1], pin=pin,
        registry_source=items[3], endpoints=items[4],
    )


def assert_forbidden(result):
    assert result.stale_result_reusable is False
    assert result.production_authorized is False
    assert result.decision_authority is False
    assert result.real_pilot_admitted is False
    assert result.operational_path == "FORBIDDEN"


def test_demo_recovers_only_after_fresh_chain_revalidation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    output = run()
    assert output["verification"] == "F6_8_SAFE_RECOVERY_SYNTHETIC_PASS"
    assert output["recovered"] == 1
    assert output["stale_result_reusable"] is False
    assert output["fresh_chain_revalidated"] is True
    assert output["production_authorized"] is False
    assert output["operational_path"] == "FORBIDDEN"


def test_successful_recovery_supersedes_stop_but_never_reuses_stale_receipt(tmp_path):
    items = stopped_case(tmp_path)
    pin, manifest = recovered_inputs(items)
    result = recover(items, pin, manifest)
    assert result.status == "SYNTHETIC_RECOVERY_REVALIDATED"
    assert result.fresh_chain_revalidated is True
    assert result.supersedes_safe_stop is True
    assert result.safe_stop_fingerprint == items[7].result_fingerprint
    assert result.stale_result_fingerprint == items[6].result_fingerprint
    assert result.fresh_result_fingerprint is not None
    assert_forbidden(result)


def test_recovery_without_safe_stop_is_rejected(tmp_path):
    items = stopped_case(tmp_path)
    pin, manifest = recovered_inputs(items)
    fake = replace(items[7], status="SYNTHETIC_CHAIN_REVALIDATED")
    with pytest.raises(RecoveryError, match="F6_7_SAFE_STOP_REQUIRED"):
        recover_after_safe_stop(
            stopped=fake, stale=items[6], manifest=manifest,
            prepared=items[0], request=items[1], pin=pin,
            registry_source=items[3], endpoints=items[4],
        )


def test_wrong_stale_receipt_cannot_be_attached_to_safe_stop(tmp_path):
    items = stopped_case(tmp_path)
    pin, manifest = recovered_inputs(items)
    foreign = replace(items[6], result_fingerprint="0" * 64)
    with pytest.raises(RecoveryError, match="SAFE_STOP_HISTORY_MISMATCH_OR_PROMOTION"):
        recover_after_safe_stop(
            stopped=items[7], stale=foreign, manifest=manifest,
            prepared=items[0], request=items[1], pin=pin,
            registry_source=items[3], endpoints=items[4],
        )


def test_unresolved_provider_failure_keeps_recovery_blocked(tmp_path):
    items = stopped_case(tmp_path)
    pin, manifest = recovered_inputs(items)
    source = items[4]["IDENTITY"].client
    def interrupted(*args, **kwargs):
        raise RuntimeError("RECOVERY_PROVIDER_STILL_DOWN")
    source.resolve_identity = interrupted
    result = recover(items, pin, manifest)
    assert result.status == "RECOVERY_BLOCKED"
    assert result.fresh_chain_revalidated is False
    assert result.supersedes_safe_stop is False
    assert "RECOVERY_PROVIDER_STILL_DOWN" in result.failure_code
    assert_forbidden(result)


def test_fresh_registry_pin_and_manifest_are_mandatory(tmp_path):
    items = stopped_case(tmp_path)
    fresh_pin, fresh_manifest = recovered_inputs(items)
    result = recover(items, items[2], items[5])
    assert result.status == "RECOVERY_BLOCKED"
    assert "ONBOARDING_STALE_OR_REVOKED_REVISION" in result.failure_code
    assert_forbidden(result)
    result = recover(items, fresh_pin, items[5])
    assert result.status == "RECOVERY_BLOCKED"
    assert result.failure_code == "F6_8_FRESH_CONTEXT_MISMATCH"
    assert_forbidden(result)
    assert fresh_manifest.registry_digest == fresh_pin.expected_digest


def test_context_drift_stop_requires_new_chain_not_recovery(tmp_path):
    items = stopped_case(tmp_path)
    foreign_request = items[1].model_copy(update={"data_snapshot_id": "FOREIGN"})
    context_stop = revalidate_before_rehearsal_reuse(
        previous=items[6], manifest=items[5], prepared=items[0],
        request=foreign_request, pin=items[2],
        registry_source=items[3], endpoints=items[4],
    )
    assert context_stop.status == "SAFE_STOPPED"
    assert context_stop.failure_stage == "CONTEXT_REBIND"
    result = recover_after_safe_stop(
        stopped=context_stop,
        stale=items[6],
        manifest=items[5],
        prepared=items[0],
        request=items[1],
        pin=items[2],
        registry_source=items[3],
        endpoints=items[4],
    )
    assert result.status == "RECOVERY_BLOCKED_NEW_CHAIN_REQUIRED"
    assert result.failure_code == "F6_8_CONTEXT_DRIFT_REQUIRES_NEW_CHAIN"
    assert result.supersedes_safe_stop is False
    assert_forbidden(result)


def test_recovery_receipt_is_deterministic_for_same_fresh_state(tmp_path):
    items = stopped_case(tmp_path)
    pin, manifest = recovered_inputs(items)
    first = recover(items, pin, manifest)
    second = recover(items, pin, manifest)
    assert first.status == second.status == "SYNTHETIC_RECOVERY_REVALIDATED"
    assert first.result_fingerprint == second.result_fingerprint
    assert first.fresh_result_fingerprint == second.fresh_result_fingerprint


@pytest.mark.parametrize("field", (
    "real_pilot_admitted", "real_company_authenticated",
    "real_document_authenticated", "real_human_authorized",
    "production_authorized", "decision_authority",
))
def test_forged_safe_stop_authority_cannot_enter_recovery(tmp_path, field):
    items = stopped_case(tmp_path)
    pin, manifest = recovered_inputs(items)
    forged = replace(items[7], **{field: True})
    with pytest.raises(RecoveryError, match="SAFE_STOP_HISTORY_MISMATCH_OR_PROMOTION"):
        recover_after_safe_stop(
            stopped=forged, stale=items[6], manifest=manifest,
            prepared=items[0], request=items[1], pin=pin,
            registry_source=items[3], endpoints=items[4],
        )


def test_safe_stop_from_another_scope_cannot_be_recovered(tmp_path):
    items = stopped_case(tmp_path)
    pin, manifest = recovered_inputs(items)
    forged = replace(items[7], company_id="EXTERNAL_COMPANY_B")
    result = recover_after_safe_stop(
        stopped=forged, stale=items[6], manifest=manifest,
        prepared=items[0], request=items[1], pin=pin,
        registry_source=items[3], endpoints=items[4],
    )
    assert result.status == "RECOVERY_BLOCKED"
    assert result.failure_code == "F6_8_SAFE_STOP_SCOPE_MISMATCH"
    assert result.supersedes_safe_stop is False
    assert_forbidden(result)
