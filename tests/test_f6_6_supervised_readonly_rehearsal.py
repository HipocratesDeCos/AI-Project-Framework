"""F6.6 adversarial preflight: rehearsed does not mean authenticated or admitted."""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
for fixture in (
    "f6_2_external_company_adapter",
    "f6_3_documentary_boundary_consumer",
    "f6_4_custody_consumer",
    "f6_5_onboarding_consumer",
):
    sys.path.insert(0, str(ROOT / "tests" / "fixtures" / fixture / "src"))

from eios_onboarding_example.demo import fixture as fixture_company  # noqa: E402
from eios_onboarding_example.onboarding import review_with_onboarded_providers  # noqa: E402
from eios_onboarding_example.pilot import (  # noqa: E402
    REQUIREMENTS, RehearsalChecklistItem, RehearsalManifest,
    PilotReadinessError, assess_read_only_rehearsal,
)
from eios_onboarding_example.pilot_demo import manifest_for, run  # noqa: E402


def ready(tmp_path, company="EXTERNAL_COMPANY_A"):
    folder = tmp_path / company
    folder.mkdir()
    prepared, request, pin, registry, endpoints = fixture_company(company, folder)
    receipt = review_with_onboarded_providers(
        prepared=prepared, request=request, pin=pin,
        registry_source=registry, endpoints=endpoints,
    )
    manifest = manifest_for(pin, request)
    return [manifest, pin, request, receipt, registry, endpoints]


def assess(items):
    return assess_read_only_rehearsal(
        manifest=items[0], pin=items[1], request=items[2],
        technical_review=items[3],
    )


def test_demo_is_complete_for_one_company_but_still_never_real(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    output = run()
    assert output["verification"] == "F6_6_SUPERVISED_SYNTHETIC_REHEARSAL_CONFORMANCE_PASS"
    assert output["companies"] == 2
    assert output["complete_synthetic_rehearsals"] == 1
    assert output["blocked_incomplete_rehearsals"] == 1
    assert output["required_checks"] == len(REQUIREMENTS) == 12
    for key in ("real_pilot_admitted", "production_authorized", "decision_authority"):
        assert output[key] is False
    assert output["operational_path"] == "FORBIDDEN"
    for receipt in output["receipts"]:
        assert receipt["real_pilot_admitted"] is False
        assert receipt["real_company_authenticated"] is False
        assert receipt["real_document_authenticated"] is False
        assert receipt["real_human_authorized"] is False
        assert receipt["decision_authority"] is False
        assert receipt["operational_path"] == "FORBIDDEN"


def test_complete_rehearsal_retains_prohibition_and_never_calls_providers_again(tmp_path):
    items = ready(tmp_path)
    before_registry = items[4].calls
    before_identity = items[5]["IDENTITY"].client.calls
    result = assess(items)
    assert result.status == "SYNTHETIC_REHEARSAL_COMPLETE"
    assert result.synthetic_rehearsal_complete is True
    assert result.missing == result.unverified == ()
    assert result.observed == REQUIREMENTS
    assert result.production_authorized is False
    assert result.real_pilot_admitted is False
    assert result.operational_path == "FORBIDDEN"
    assert result.result_fingerprint == assess(items).result_fingerprint
    assert items[4].calls == before_registry
    assert items[5]["IDENTITY"].client.calls == before_identity


def test_missing_and_unverified_are_distinct_and_cannot_be_marked_complete(tmp_path):
    items = ready(tmp_path)
    items[0] = manifest_for(
        items[1], items[2],
        missing=("ACCESS_REVOCATION_REHEARSAL",),
        unverified=("TRACE_AND_TRUSTED_TIME",),
    )
    result = assess(items)
    assert result.status == "REHEARSAL_INCOMPLETE"
    assert result.synthetic_rehearsal_complete is False
    assert result.missing == ("ACCESS_REVOCATION_REHEARSAL",)
    assert result.unverified == ("TRACE_AND_TRUSTED_TIME",)
    assert len(result.observed) == 10
    assert result.real_pilot_admitted is False


@pytest.mark.parametrize("field,value", (
    ("company_id", "FOREIGN"),
    ("project_id", "FOREIGN"),
    ("data_snapshot_id", "FOREIGN"),
    ("registry_digest", "0" * 64),
    ("registry_revision", 2),
))
def test_manifest_different_from_technical_case_refused(tmp_path, field, value):
    items = ready(tmp_path)
    items[0] = replace(items[0], **{field: value})
    with pytest.raises(PilotReadinessError, match="REHEARSAL_TENANT_SNAPSHOT_OR_PIN_MISMATCH"):
        assess(items)


def test_host_pin_and_review_timestamp_must_correspond(tmp_path):
    items = ready(tmp_path)
    items[1] = replace(items[1], expected_digest="0" * 64)
    with pytest.raises(PilotReadinessError, match="REHEARSAL_TENANT_SNAPSHOT_OR_PIN_MISMATCH"):
        assess(items)
    # A pin replacement is not an approved registry revision; no provider calls occur.


@pytest.mark.parametrize("field,value", (
    ("purpose", "PRESENTED_OPERATIONAL"),
    ("mode", "LIVE_OPERATIONAL_PILOT"),
    ("observer_ref", "REAL_REVIEWER_01"),
    ("rehearsal_ref", "REAL_PILOT_01"),
))
def test_real_authority_and_pilot_labels_are_rejected(tmp_path, field, value):
    items = ready(tmp_path)
    expected = (
        "OPERATIONAL_PILOT_PROMOTION_FORBIDDEN"
        if field in ("purpose", "mode") else
        "REAL_OBSERVER_OR_REHEARSAL_CLAIM_FORBIDDEN"
    )
    with pytest.raises(PilotReadinessError, match=expected):
        replace(items[0], **{field: value})


def test_naive_timestamp_and_scope_mismatch_are_rejected(tmp_path):
    items = ready(tmp_path)
    with pytest.raises(PilotReadinessError, match="TRUSTED_AWARE_TIME_REQUIRED"):
        replace(items[0], reviewed_at=items[0].reviewed_at.replace(tzinfo=None))
    items[0] = replace(items[0], reviewed_at=items[0].reviewed_at + timedelta(minutes=1))
    with pytest.raises(PilotReadinessError, match="REHEARSAL_TENANT_SNAPSHOT_OR_PIN_MISMATCH"):
        assess(items)


@pytest.mark.parametrize("status", ("VERIFIED", "CONFIRMED_REAL", "PRESENTED_OPERATIONAL", ""))
def test_no_real_document_claim_is_permitted_in_synthetic_checklist(status):
    with pytest.raises(PilotReadinessError, match="INVALID_PILOT_EVIDENCE_STATUS"):
        RehearsalChecklistItem(
            "COMPANY_AND_PROJECT_MANDATE", status=status,
            support_ref="SYNTHETIC_PROOF",
        )


def test_missing_or_unverified_cannot_carry_misleading_support_reference():
    for state in ("MISSING", "UNVERIFIED"):
        with pytest.raises(PilotReadinessError, match="UNVERIFIED_OR_MISSING_SUPPORT_CANNOT_BE_REFERENCED"):
            RehearsalChecklistItem(
                requirement_id=REQUIREMENTS[0], status=state,
                support_ref="SYNTHETIC_DOC",
            )
    with pytest.raises(PilotReadinessError, match="REAL_EVIDENCE_CLAIM_FORBIDDEN"):
        RehearsalChecklistItem(
            requirement_id=REQUIREMENTS[0],
            status="SYNTHETIC_REHEARSED",
            support_ref="AUTHENTICATED_CERTIFICATE",
        )


def test_duplicate_or_missing_checks_and_repeated_references_are_rejected(tmp_path):
    items = ready(tmp_path)
    source = items[0]
    with pytest.raises(PilotReadinessError, match="INCOMPLETE_OR_DUPLICATE_PILOT_CHECKLIST"):
        replace(source, checks=source.checks[:-1])
    with pytest.raises(PilotReadinessError, match="INCOMPLETE_OR_DUPLICATE_PILOT_CHECKLIST"):
        replace(source, checks=tuple(reversed(source.checks)))
    duplicate_ref = replace(source.checks[1], support_ref=source.checks[0].support_ref)
    checks = (source.checks[0], duplicate_ref, *source.checks[2:])
    with pytest.raises(PilotReadinessError, match="DUPLICATE_PILOT_SUPPORT_REF"):
        replace(source, checks=checks)


@pytest.mark.parametrize("flag", (
    "production_authorized", "decision_authority", "real_provider_connected",
    "real_enterprise_authenticated", "real_document_authenticated",
    "real_reviewer_authorized",
))
def test_forged_f65_operational_or_real_claim_is_blocked(tmp_path, flag):
    items = ready(tmp_path)
    items[3] = replace(items[3], **{flag: True})
    with pytest.raises(PilotReadinessError, match="F6_5_OR_F6_3_AUTHORITY_PROMOTION_OR_MISMATCH"):
        assess(items)


@pytest.mark.parametrize("flag", (
    "production_authorized", "decision_authority",
    "real_company_authenticated", "real_document_authenticated",
    "real_human_authorized",
))
def test_forged_f63_documentary_receipt_is_blocked(tmp_path, flag):
    items = ready(tmp_path)
    altered = replace(items[3].review_receipt, **{flag: True})
    items[3] = replace(items[3], review_receipt=altered)
    with pytest.raises(PilotReadinessError, match="F6_5_OR_F6_3_AUTHORITY_PROMOTION_OR_MISMATCH"):
        assess(items)


@pytest.mark.parametrize("field,value", (
    ("document_ref", "OTHER_DOC"),
    ("source_sha256", "0" * 64),
    ("document_sha256", "0" * 64),
    ("company_id", "EXTERNAL_COMPANY_B"),
))
def test_forged_receipt_scope_and_document_bytes_are_blocked(tmp_path, field, value):
    items = ready(tmp_path)
    altered = replace(items[3].review_receipt, **{field: value})
    items[3] = replace(items[3], review_receipt=altered)
    with pytest.raises(PilotReadinessError, match="F6_5_OR_F6_3_AUTHORITY_PROMOTION_OR_MISMATCH"):
        assess(items)


def test_company_b_manifest_never_matches_company_a_receipt(tmp_path):
    a = ready(tmp_path, company="EXTERNAL_COMPANY_A")
    b = ready(tmp_path, company="EXTERNAL_COMPANY_B")
    a[3] = b[3]
    with pytest.raises(PilotReadinessError, match="REHEARSAL_TENANT_SNAPSHOT_OR_PIN_MISMATCH"):
        assess(a)
