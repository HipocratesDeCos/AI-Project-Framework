"""F6.10 independent retry/idempotency demonstration."""
from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

from eios_custody_example.custody import SyntheticCustodyVault

from .demo import fixture
from .onboarding import (
    PinnedOnboarding,
    fingerprint_provider_snapshot,
    review_with_onboarded_providers,
)
from .pilot import assess_read_only_rehearsal
from .pilot_demo import manifest_for
from .safe_stop import revalidate_before_rehearsal_reuse
from .recovery import recover_after_safe_stop
from .resilience import record_lifecycle_event_retry_safe
from .lifecycle import verify_lifecycle_history


def run() -> dict:
    root = Path.cwd() / "f610-retry-demo"
    root.mkdir(exist_ok=False)
    evidence = root / "evidence"
    journal_root = root / "journal"
    evidence.mkdir()
    journal_root.mkdir()

    prepared, request, pin, registry, endpoints = fixture(
        "EXTERNAL_COMPANY_A", evidence,
    )
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
    assert stopped.status == "SAFE_STOPPED"

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
    assert recovery.status == "SYNTHETIC_RECOVERY_REVALIDATED"

    vault = SyntheticCustodyVault(journal_root)

    first_created = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=baseline,
        baseline_manifest=old_manifest,
    )
    first_retry = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=baseline,
        baseline_manifest=old_manifest,
    )
    assert first_created.disposition == "CREATED"
    assert first_retry.disposition == "REUSED_IDENTICAL"
    assert first_retry.receipt == first_created.receipt

    second_created = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=stopped,
        previous=first_retry.receipt,
    )
    second_retry = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=stopped,
        previous=first_retry.receipt,
    )
    assert second_created.disposition == "CREATED"
    assert second_retry.disposition == "REUSED_IDENTICAL"

    third_created = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=recovery,
        previous=second_retry.receipt,
    )
    third_retry = record_lifecycle_event_retry_safe(
        vault=vault,
        request=request,
        source=recovery,
        previous=second_retry.receipt,
    )
    assert third_created.disposition == "CREATED"
    assert third_retry.disposition == "REUSED_IDENTICAL"

    receipts = (
        first_retry.receipt,
        second_retry.receipt,
        third_retry.receipt,
    )
    verified = verify_lifecycle_history(
        vault=vault,
        request=request,
        receipts=receipts,
    )
    assert verified.status == "SYNTHETIC_LIFECYCLE_HISTORY_VERIFIED"
    assert len(list(journal_root.glob("*.json"))) == 3

    return {
        "verification": "F6_10_IDEMPOTENT_RETRY_SYNTHETIC_PASS",
        "created": 3,
        "reused_identical": 3,
        "event_count": verified.event_count,
        "history_status": verified.status,
        "head_sha256": verified.head_sha256,
        "retry_receipts": [
            asdict(first_retry),
            asdict(second_retry),
            asdict(third_retry),
        ],
        "production_authorized": False,
        "decision_authority": False,
        "real_pilot_admitted": False,
        "operational_path": "FORBIDDEN",
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
