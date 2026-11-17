"""F6.9 independently installed synthetic lifecycle journal demonstration."""
from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

from eios_custody_example.custody import SyntheticCustodyVault

from .demo import fixture
from .onboarding import (
    PinnedOnboarding, fingerprint_provider_snapshot,
    review_with_onboarded_providers,
)
from .pilot import assess_read_only_rehearsal
from .pilot_demo import manifest_for
from .safe_stop import revalidate_before_rehearsal_reuse
from .recovery import recover_after_safe_stop
from .lifecycle import record_lifecycle_event, verify_lifecycle_history


def run() -> dict:
    root = Path.cwd() / "f69-lifecycle-demo"
    root.mkdir(exist_ok=False)
    evidence = root / "evidence"
    journal_root = root / "journal"
    evidence.mkdir()
    journal_root.mkdir()

    prepared, request, pin, registry, endpoints = fixture(
        "EXTERNAL_COMPANY_A", evidence,
    )
    technical = review_with_onboarded_providers(
        prepared=prepared, request=request, pin=pin,
        registry_source=registry, endpoints=endpoints,
    )
    old_manifest = manifest_for(pin, request)
    baseline = assess_read_only_rehearsal(
        manifest=old_manifest, pin=pin, request=request,
        technical_review=technical,
    )

    registry.snapshot = replace(
        registry.snapshot,
        revision=registry.snapshot.revision + 1,
        registrations=tuple(
            replace(row, enabled=False) if row.role == "REVIEW_PERMISSION" else row
            for row in registry.snapshot.registrations
        ),
    )
    stopped = revalidate_before_rehearsal_reuse(
        previous=baseline, manifest=old_manifest, prepared=prepared,
        request=request, pin=pin, registry_source=registry, endpoints=endpoints,
    )
    assert stopped.status == "SAFE_STOPPED"

    registry.snapshot = replace(
        registry.snapshot,
        registrations=tuple(
            replace(row, enabled=True) for row in registry.snapshot.registrations
        ),
    )
    fresh_pin = PinnedOnboarding(
        project_id=registry.snapshot.project_id,
        company_id=registry.snapshot.company_id,
        expected_revision=registry.snapshot.revision,
        expected_digest=fingerprint_provider_snapshot(registry.snapshot),
    )
    fresh_manifest = manifest_for(fresh_pin, request)
    recovery = recover_after_safe_stop(
        stopped=stopped, stale=baseline, manifest=fresh_manifest,
        prepared=prepared, request=request, pin=fresh_pin,
        registry_source=registry, endpoints=endpoints,
    )
    assert recovery.status == "SYNTHETIC_RECOVERY_REVALIDATED"

    vault = SyntheticCustodyVault(journal_root)
    first = record_lifecycle_event(
        vault=vault, request=request, source=baseline,
        baseline_manifest=old_manifest,
    )
    second = record_lifecycle_event(
        vault=vault, request=request, source=stopped, previous=first,
    )
    third = record_lifecycle_event(
        vault=vault, request=request, source=recovery, previous=second,
    )
    verified = verify_lifecycle_history(
        vault=vault, request=request, receipts=(first, second, third),
    )
    assert verified.status == "SYNTHETIC_LIFECYCLE_HISTORY_VERIFIED"
    assert verified.head_sha256 == third.event_sha256
    assert len(list(journal_root.glob("*.json"))) == 3

    return {
        "verification": "F6_9_LIFECYCLE_INTEGRITY_SYNTHETIC_PASS",
        "event_count": verified.event_count,
        "history_status": verified.status,
        "head_sha256": verified.head_sha256,
        "receipts": [asdict(first), asdict(second), asdict(third)],
        "production_authorized": False,
        "decision_authority": False,
        "real_pilot_admitted": False,
        "operational_path": "FORBIDDEN",
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
