"""F6.8 independently installed synthetic recovery demonstration."""
from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

from .demo import fixture
from .onboarding import (
    PinnedOnboarding, fingerprint_provider_snapshot,
    review_with_onboarded_providers,
)
from .pilot import assess_read_only_rehearsal
from .pilot_demo import manifest_for
from .safe_stop import revalidate_before_rehearsal_reuse
from .recovery import recover_after_safe_stop


def _stopped(company: str, root: Path):
    prepared, request, pin, registry, endpoints = fixture(company, root)
    technical = review_with_onboarded_providers(
        prepared=prepared, request=request, pin=pin,
        registry_source=registry, endpoints=endpoints,
    )
    old_manifest = manifest_for(pin, request)
    stale = assess_read_only_rehearsal(
        manifest=old_manifest, pin=pin, request=request,
        technical_review=technical,
    )
    revoked = replace(
        registry.snapshot,
        revision=registry.snapshot.revision + 1,
        registrations=tuple(
            replace(row, enabled=False) if row.role == "REVIEW_PERMISSION" else row
            for row in registry.snapshot.registrations
        ),
    )
    registry.snapshot = revoked
    stopped = revalidate_before_rehearsal_reuse(
        previous=stale, manifest=old_manifest, prepared=prepared,
        request=request, pin=pin, registry_source=registry, endpoints=endpoints,
    )
    assert stopped.status == "SAFE_STOPPED"
    return prepared, request, pin, registry, endpoints, old_manifest, stale, stopped


def run() -> dict:
    root = Path.cwd() / "f68-recovery-synthetic-custody"
    root.mkdir(exist_ok=False)
    items = _stopped("EXTERNAL_COMPANY_A", root)

    restored = replace(
        items[3].snapshot,
        registrations=tuple(replace(row, enabled=True) for row in items[3].snapshot.registrations),
    )
    items[3].snapshot = restored
    new_pin = PinnedOnboarding(
        project_id=restored.project_id,
        company_id=restored.company_id,
        expected_revision=restored.revision,
        expected_digest=fingerprint_provider_snapshot(restored),
    )
    new_manifest = manifest_for(new_pin, items[1])
    recovered = recover_after_safe_stop(
        stopped=items[7], stale=items[6], manifest=new_manifest,
        prepared=items[0], request=items[1], pin=new_pin,
        registry_source=items[3], endpoints=items[4],
    )
    assert recovered.status == "SYNTHETIC_RECOVERY_REVALIDATED"
    assert recovered.stale_result_reusable is False
    assert recovered.fresh_chain_revalidated is True
    assert recovered.supersedes_safe_stop is True
    assert recovered.fresh_result_fingerprint is not None

    return {
        "verification": "F6_8_SAFE_RECOVERY_SYNTHETIC_PASS",
        "recovered": 1,
        "stale_result_reusable": False,
        "fresh_chain_revalidated": True,
        "receipt": asdict(recovered),
        "real_pilot_admitted": False,
        "production_authorized": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
