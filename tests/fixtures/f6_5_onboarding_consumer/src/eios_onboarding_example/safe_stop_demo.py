"""F6.7 independently installed integral fail-closed demonstration."""
from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

from .demo import fixture
from .onboarding import review_with_onboarded_providers
from .pilot import assess_read_only_rehearsal
from .pilot_demo import manifest_for
from .safe_stop import revalidate_before_rehearsal_reuse


def _ready(company: str, root: Path):
    prepared, request, pin, registry, endpoints = fixture(company, root)
    technical = review_with_onboarded_providers(
        prepared=prepared, request=request, pin=pin,
        registry_source=registry, endpoints=endpoints,
    )
    manifest = manifest_for(pin, request)
    previous = assess_read_only_rehearsal(
        manifest=manifest, pin=pin, request=request,
        technical_review=technical,
    )
    assert previous.synthetic_rehearsal_complete is True
    return prepared, request, pin, registry, endpoints, manifest, previous


def run() -> dict:
    root = Path.cwd() / "f67-safe-stop-synthetic-custody"
    root.mkdir(exist_ok=False)

    healthy = _ready("EXTERNAL_COMPANY_A", root)
    healthy_result = revalidate_before_rehearsal_reuse(
        previous=healthy[6], manifest=healthy[5], prepared=healthy[0],
        request=healthy[1], pin=healthy[2],
        registry_source=healthy[3], endpoints=healthy[4],
    )
    assert healthy_result.status == "SYNTHETIC_CHAIN_REVALIDATED"

    revoked = _ready("EXTERNAL_COMPANY_B", root)
    snapshot = revoked[3].snapshot
    changed = replace(
        snapshot,
        revision=snapshot.revision + 1,
        registrations=tuple(
            replace(row, enabled=False) if row.role == "REVIEW_PERMISSION" else row
            for row in snapshot.registrations
        ),
    )
    revoked[3].snapshot = changed
    revoked_result = revalidate_before_rehearsal_reuse(
        previous=revoked[6], manifest=revoked[5], prepared=revoked[0],
        request=revoked[1], pin=revoked[2],
        registry_source=revoked[3], endpoints=revoked[4],
    )
    assert revoked_result.status == "SAFE_STOPPED"
    assert revoked_result.previous_result_invalidated is True
    assert revoked_result.fresh_revalidation_passed is False

    results = [asdict(healthy_result), asdict(revoked_result)]
    assert all(row["production_authorized"] is False for row in results)
    assert all(row["decision_authority"] is False for row in results)
    assert all(row["operational_path"] == "FORBIDDEN" for row in results)
    return {
        "verification": "F6_7_INTEGRAL_SAFE_STOP_SYNTHETIC_PASS",
        "healthy_revalidated": 1,
        "safe_stopped": 1,
        "previous_results_invalidated": 1,
        "receipts": results,
        "real_pilot_admitted": False,
        "production_authorized": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
