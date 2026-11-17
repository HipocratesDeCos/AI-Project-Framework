"""F6.6 independently installed rehearsal demo: no real pilot or decision.

Executes existing F6.5 onboarding for two synthetic companies and binds
an explicit, complete checklist vs a deliberately incomplete checklist.
Neither outcome enables any operational path.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

from .demo import fixture
from .onboarding import review_with_onboarded_providers
from .pilot import (
    REQUIREMENTS, RehearsalChecklistItem, RehearsalManifest,
    assess_read_only_rehearsal,
)


def manifest_for(pin, request, *, missing=(), unverified=()) -> RehearsalManifest:
    """Synthetic evidence references only; not proof of a human review."""
    if set(missing) & set(unverified):
        raise ValueError("A checklist item cannot have conflicting outcomes")
    return RehearsalManifest(
        project_id=pin.project_id,
        company_id=pin.company_id,
        data_snapshot_id=request.data_snapshot_id,
        registry_digest=pin.expected_digest,
        registry_revision=pin.expected_revision,
        rehearsal_ref="SYNTHETIC_F66_REHEARSAL_" + pin.company_id,
        observer_ref="SYNTHETIC_F66_OBSERVER_" + pin.company_id,
        reviewed_at=request.reviewed_at,
        checks=tuple(
            RehearsalChecklistItem(
                requirement_id=name,
                status=(
                    "MISSING" if name in missing else
                    "UNVERIFIED" if name in unverified else
                    "SYNTHETIC_REHEARSED"
                ),
                support_ref=(
                    None if name in missing or name in unverified
                    else "SYNTHETIC_F66_" + name + "_" + pin.company_id
                ),
            )
            for name in REQUIREMENTS
        ),
    )


def run() -> dict:
    location = Path.cwd() / "f66-readonly-synthetic-custody"
    location.mkdir(exist_ok=False)
    results = []
    for company in ("EXTERNAL_COMPANY_A", "EXTERNAL_COMPANY_B"):
        prepared, request, pin, registry, endpoints = fixture(company, location)
        technical = review_with_onboarded_providers(
            prepared=prepared,
            request=request, pin=pin,
            registry_source=registry, endpoints=endpoints,
        )
        manifest = manifest_for(
            pin, request,
            missing=() if company.endswith("_A") else ("ACCESS_REVOCATION_REHEARSAL",),
            unverified=() if company.endswith("_A") else ("TRACE_AND_TRUSTED_TIME",),
        )
        result = assess_read_only_rehearsal(
            manifest=manifest, pin=pin, request=request,
            technical_review=technical,
        )
        assert result.operational_path == "FORBIDDEN"
        assert result.production_authorized is False
        assert result.real_pilot_admitted is False
        assert result.decision_authority is False
        if company.endswith("_A"):
            assert result.status == "SYNTHETIC_REHEARSAL_COMPLETE"
            assert result.synthetic_rehearsal_complete is True
        else:
            assert result.status == "REHEARSAL_INCOMPLETE"
            assert result.synthetic_rehearsal_complete is False
            assert result.missing == ("ACCESS_REVOCATION_REHEARSAL",)
            assert result.unverified == ("TRACE_AND_TRUSTED_TIME",)
        results.append(asdict(result))
    assert len({r["company_id"] for r in results}) == 2
    assert len({r["result_fingerprint"] for r in results}) == 2
    assert len(list(location.glob("*.json"))) == 2
    return {
        "verification": "F6_6_SUPERVISED_SYNTHETIC_REHEARSAL_CONFORMANCE_PASS",
        "companies": 2,
        "complete_synthetic_rehearsals": 1,
        "blocked_incomplete_rehearsals": 1,
        "required_checks": len(REQUIREMENTS),
        "receipts": results,
        "real_provider_connection": "NOT_TESTED",
        "real_company_identity": "NOT_TESTED",
        "real_documentary_support": "NOT_TESTED",
        "real_human_supervision": "NOT_TESTED",
        "real_pilot_admitted": False,
        "production_authorized": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
