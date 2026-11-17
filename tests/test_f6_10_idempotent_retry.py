"""F6.10 — idempotency, retry, restart and replay safety."""
from __future__ import annotations

from dataclasses import replace
import json
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

from eios_custody_example.custody import SyntheticCustodyVault  # noqa: E402
from eios_onboarding_example.demo import fixture  # noqa: E402
from eios_onboarding_example.onboarding import (  # noqa: E402
    PinnedOnboarding,
    fingerprint_provider_snapshot,
    review_with_onboarded_providers,
)
from eios_onboarding_example.pilot import assess_read_only_rehearsal  # noqa: E402
from eios_onboarding_example.pilot_demo import manifest_for  # noqa: E402
from eios_onboarding_example.safe_stop import revalidate_before_rehearsal_reuse  # noqa: E402
from eios_onboarding_example.recovery import recover_after_safe_stop  # noqa: E402
from eios_onboarding_example.lifecycle import verify_lifecycle_history  # noqa: E402
from eios_onboarding_example.resilience import (  # noqa: E402
    RetrySafetyError,
    record_lifecycle_event_retry_safe,
)
from eios_onboarding_example.retry_demo import run  # noqa: E402


def case(tmp_path, company="EXTERNAL_COMPANY_A"):
    evidence = tmp_path / ("evidence-" + company)
    journal = tmp_path / ("journal-" + company)
    evidence.mkdir()
    journal.mkdir()

    prepared, request, pin, registry, endpoints = fixture(company, evidence)
    technical = review_with_onboarded_providers(
        prepared=prepared,
        request=request,
        pin=pin,
        registry_source=registry,
        endpoints=endpoints,
    )
    old_manifest = manifest_for(pin, request)
    baseline = assess_read_only_rehearsal(
        manifest=old_manifest,
        pin=pin,
        request=request,
        technical_review=technical,
    )

    registry.snapshot = replace(registry.snapshot, revision=2)
    stopped = revalidate_before_rehearsal_reuse(
        previous=baseline,
        manifest=old_manifest,
        prepared=prepared,
        request=request,
        pin=pin,
        registry_source=registry,
        endpoints=endpoints,
    )
    fresh_pin = PinnedOnboarding(
        project_id=registry.snapshot.project_id,
        company_id=registry.snapshot.company_id,
        expected_revision=registry.snapshot.revision,
        expected_digest=fingerprint_provider_snapshot(registry.snapshot),
    )
    recovery = recover_after_safe_stop(
        stopped=stopped,
        stale=baseline,
        manifest=manifest_for(fresh_pin, request),
        prepared=prepared,
        request=request,
        pin=fresh_pin,
        registry_source=registry,
        endpoints=endpoints,
    )
    return (
        request,
        old_manifest,
        SyntheticCustodyVault(journal),
        baseline,
        stopped,
        recovery,
        journal,
    )


def write_all(request, manifest, vault, baseline, stopped, recovery):
    first = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=baseline,
        baseline_manifest=manifest,
    )
    second = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=stopped,
        previous=first.receipt,
    )
    third = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=recovery,
        previous=second.receipt,
    )
    return first, second, third


def test_demo_proves_create_then_identical_retry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    output = run()
    assert output["verification"] == "F6_10_IDEMPOTENT_RETRY_SYNTHETIC_PASS"
    assert output["created"] == 3
    assert output["reused_identical"] == 3
    assert output["event_count"] == 3
    assert output["production_authorized"] is False
    assert output["decision_authority"] is False
    assert output["operational_path"] == "FORBIDDEN"


def test_identical_retry_is_idempotent_and_does_not_add_files(tmp_path):
    request, manifest, vault, baseline, stopped, recovery, journal = case(tmp_path)
    first, second, third = write_all(
        request, manifest, vault, baseline, stopped, recovery,
    )
    before = sorted(p.name for p in journal.glob("*.json"))
    retried = write_all(
        request, manifest, vault, baseline, stopped, recovery,
    )
    after = sorted(p.name for p in journal.glob("*.json"))
    assert before == after
    assert len(after) == 3
    assert [x.disposition for x in retried] == [
        "REUSED_IDENTICAL", "REUSED_IDENTICAL", "REUSED_IDENTICAL",
    ]
    assert [x.receipt for x in retried] == [
        first.receipt, second.receipt, third.receipt,
    ]


def test_restart_after_ack_loss_reconstructs_exact_receipt(tmp_path):
    request, manifest, vault, baseline, _, _, _ = case(tmp_path)
    created = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=baseline,
        baseline_manifest=manifest,
    )
    del created
    restarted = SyntheticCustodyVault(vault.root)
    recovered = record_lifecycle_event_retry_safe(
        vault=restarted,
        request=request,
        source=baseline,
        baseline_manifest=manifest,
    )
    assert recovered.disposition == "REUSED_IDENTICAL"


def test_full_history_remains_verifiable_after_retries(tmp_path):
    request, manifest, vault, baseline, stopped, recovery, _ = case(tmp_path)
    created = write_all(request, manifest, vault, baseline, stopped, recovery)
    retried = write_all(request, manifest, vault, baseline, stopped, recovery)
    verification = verify_lifecycle_history(
        vault=vault,
        request=request,
        receipts=tuple(x.receipt for x in retried),
    )
    assert verification.status == "SYNTHETIC_LIFECYCLE_HISTORY_VERIFIED"
    assert verification.head_sha256 == created[2].receipt.event_sha256


def test_conflicting_retry_same_stage_is_rejected(tmp_path):
    request, manifest, vault, baseline, _, _, _ = case(tmp_path)
    original = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=baseline,
        baseline_manifest=manifest,
    )
    forged = replace(baseline, result_fingerprint="0" * 64)
    with pytest.raises(RetrySafetyError):
        record_lifecycle_event_retry_safe(
            vault=vault,
            request=request,
            source=forged,
            baseline_manifest=manifest,
        )
    assert original.disposition == "CREATED"


def test_tampered_existing_record_is_not_repaired(tmp_path):
    request, manifest, vault, baseline, _, _, journal = case(tmp_path)
    created = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=baseline,
        baseline_manifest=manifest,
    )
    path = next(journal.glob("*.json"))
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["content_b64"] = "AAAA"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(RetrySafetyError, match="LIFECYCLE_RETRY_CONFLICT_OR_TAMPER"):
        record_lifecycle_event_retry_safe(
            vault=vault,
            request=request,
            source=baseline,
            baseline_manifest=manifest,
        )
    assert path.exists()
    assert created.receipt.event_sha256


def test_partial_or_invalid_existing_file_blocks_retry(tmp_path):
    request, manifest, vault, baseline, _, _, journal = case(tmp_path)
    first = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=baseline,
        baseline_manifest=manifest,
    )
    path = next(journal.glob("*.json"))
    path.write_bytes(b"{")
    with pytest.raises(RetrySafetyError, match="LIFECYCLE_RETRY_CONFLICT_OR_TAMPER"):
        record_lifecycle_event_retry_safe(
            vault=vault,
            request=request,
            source=baseline,
            baseline_manifest=manifest,
        )
    assert first.disposition == "CREATED"


def test_cross_company_receipt_cannot_drive_retry(tmp_path):
    request_a, manifest_a, vault_a, baseline_a, stopped_a, _, _ = case(
        tmp_path, "EXTERNAL_COMPANY_A",
    )
    request_b, manifest_b, vault_b, baseline_b, _, _, _ = case(
        tmp_path, "EXTERNAL_COMPANY_B",
    )
    first_a = record_lifecycle_event_retry_safe(
        vault=vault_a,
        request=request_a,
        source=baseline_a,
        baseline_manifest=manifest_a,
    )
    first_b = record_lifecycle_event_retry_safe(
        vault=vault_b,
        request=request_b,
        source=baseline_b,
        baseline_manifest=manifest_b,
    )
    with pytest.raises(RetrySafetyError):
        record_lifecycle_event_retry_safe(
            vault=vault_a,
            request=request_a,
            source=stopped_a,
            previous=first_b.receipt,
        )
    assert first_a.receipt.company_id != first_b.receipt.company_id


def test_forged_authority_input_remains_rejected(tmp_path):
    request, manifest, vault, baseline, _, _, _ = case(tmp_path)
    forged = replace(baseline, production_authorized=True)
    with pytest.raises(RetrySafetyError, match="INVALID_LIFECYCLE_RETRY_INPUT"):
        record_lifecycle_event_retry_safe(
            vault=vault,
            request=request,
            source=forged,
            baseline_manifest=manifest,
        )


def test_changed_manifest_same_scope_is_not_an_identical_retry(tmp_path):
    request, manifest, vault, baseline, _, _, _ = case(tmp_path)
    record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=baseline,
        baseline_manifest=manifest,
    )
    changed_check = replace(
        manifest.checks[0],
        support_ref="SYNTHETIC_RETRY_CHANGED_SUPPORT",
    )
    changed_manifest = replace(
        manifest,
        checks=(changed_check,) + manifest.checks[1:],
    )
    with pytest.raises(RetrySafetyError, match="INVALID_LIFECYCLE_RETRY_INPUT"):
        record_lifecycle_event_retry_safe(
            vault=vault,
            request=request,
            source=baseline,
            baseline_manifest=changed_manifest,
        )
