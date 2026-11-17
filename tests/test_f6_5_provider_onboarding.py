"""F6.5 adversarial gates: version pin, three provider roles, revocation and isolation."""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from hashlib import sha256
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
    sys.path.insert(0, str(ROOT / "tests/fixtures" / fixture / "src"))

from eios_onboarding_example import (  # noqa: E402
    OnboardingError, OnboardingSnapshot, PinnedOnboarding,
    ProviderEndpoint, ProviderRegistration,
    fingerprint_provider_snapshot, review_with_onboarded_providers,
)
from eios_onboarding_example.demo import fixture as make_fixture, run  # noqa: E402
from eios_evidence_boundary_example.review import DocumentaryBoundaryError  # noqa: E402


def case(tmp_path, company="EXTERNAL_COMPANY_A"):
    folder = tmp_path / ("storage_" + company)
    folder.mkdir()
    return list(make_fixture(company, folder))


def review(items):
    return review_with_onboarded_providers(
        prepared=items[0], request=items[1], pin=items[2],
        registry_source=items[3], endpoints=items[4],
    )


def test_complete_two_company_offline_technical_onboarding(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = run()
    assert result["verification"] == "F6_5_PROVIDER_ONBOARDING_SYNTHETIC_ONLY_PASS"
    assert result["companies"] == 2
    assert result["registrations_per_company"] == 3
    assert result["provider_connection"] == "TEST_DOUBLES_ONLY"
    assert result["enterprise_identity_authentication"] == "NOT_TESTED"
    assert result["documentary_authentication"] == "NOT_TESTED"
    assert result["human_review_authorization"] == "NOT_TESTED"
    assert result["production_authorized"] is False
    assert result["operational_path"] == "FORBIDDEN"
    assert len(result["receipts"]) == 2
    for receipt in result["receipts"]:
        for field in ("real_provider_connected", "real_enterprise_authenticated",
                      "real_document_authenticated", "real_reviewer_authorized",
                      "decision_authority", "production_authorized"):
            assert receipt[field] is False
        assert receipt["status"] == "SYNTHETIC_PROVIDER_ONBOARDING_READY"
        assert receipt["review_receipt"]["real_document_authenticated"] is False


def test_onboarding_is_read_only_and_rechecks_registry_before_and_after_each_provider(tmp_path):
    items = case(tmp_path)
    receipt = review(items)
    assert receipt.registry_digest == items[2].expected_digest
    assert receipt.expected_revision == 1
    assert receipt.operational_path == "FORBIDDEN"
    assert receipt.real_enterprise_authenticated is False
    assert items[3].calls == 14
    assert items[4]["IDENTITY"].client.calls == 2
    assert items[4]["REVIEW_PERMISSION"].client.calls == 2


def test_missing_registry_or_missing_role_fails_before_provider_use(tmp_path):
    items = case(tmp_path)
    items[3] = None
    with pytest.raises(OnboardingError, match="REGISTRY_SOURCE_REQUIRED"):
        review(items)
    assert all(ep.client.calls == 0 for role, ep in items[4].items()
               if role != "DOCUMENT")
    items = case(tmp_path / "new")
    items[4] = {key: ep for key, ep in items[4].items() if key != "DOCUMENT"}
    with pytest.raises(OnboardingError, match="MISSING_OR_UNDECLARED_PROVIDER_ENDPOINT"):
        review(items)
    assert items[3].calls == 0


@pytest.mark.parametrize("role", ("IDENTITY", "DOCUMENT", "REVIEW_PERMISSION"))
def test_wrong_endpoint_id_rejected_before_any_provider_call(tmp_path, role):
    items = case(tmp_path)
    items[4][role] = replace(items[4][role], provider_id="FOREIGN_PROVIDER")
    with pytest.raises(OnboardingError, match="ONBOARDING_PROVIDER_ENDPOINT_MISMATCH"):
        review(items)
    assert items[3].calls == 1
    assert items[4]["IDENTITY"].client.calls == 0
    assert items[4]["REVIEW_PERMISSION"].client.calls == 0


@pytest.mark.parametrize("field,code", (
    ("project_id", "PINNED_PROVIDER_TENANT_MISMATCH"),
    ("company_id", "PINNED_PROVIDER_TENANT_MISMATCH"),
    ("expected_revision", "ONBOARDING_STALE_OR_REVOKED_REVISION"),
    ("expected_digest", "ONBOARDING_REGISTRY_DIGEST_CHANGED"),
))
def test_host_pin_is_authoritative_not_registry_declaration(tmp_path, field, code):
    items = case(tmp_path)
    value = 2 if field == "expected_revision" else (
        "0" * 64 if field == "expected_digest" else "FOREIGN"
    )
    items[2] = replace(items[2], **{field: value})
    with pytest.raises(OnboardingError, match=code):
        review(items)
    assert items[4]["IDENTITY"].client.calls == 0


@pytest.mark.parametrize("role", ("IDENTITY", "DOCUMENT", "REVIEW_PERMISSION"))
def test_disabled_and_expired_providers_denied_even_with_host_pin_matching(tmp_path, role):
    items = case(tmp_path)
    snapshot = items[3].snapshot
    rows = tuple(
        replace(entry, enabled=False) if entry.role == role else entry
        for entry in snapshot.registrations
    )
    new = replace(snapshot, registrations=rows, revision=2)
    items[3].snapshot = new
    items[2] = replace(
        items[2], expected_revision=2,
        expected_digest=fingerprint_provider_snapshot(new),
    )
    with pytest.raises(OnboardingError, match="ONBOARDING_PROVIDER_DISABLED"):
        review(items)
    rows = tuple(
        replace(entry, valid_to=items[1].reviewed_at - timedelta(seconds=1))
        if entry.role == role else entry
        for entry in snapshot.registrations
    )
    new = replace(snapshot, registrations=rows, revision=3)
    items[3].snapshot = new
    items[2] = replace(
        items[2], expected_revision=3,
        expected_digest=fingerprint_provider_snapshot(new),
    )
    with pytest.raises(OnboardingError, match="ONBOARDING_PROVIDER_EXPIRED"):
        review(items)


def test_registered_revocation_after_identity_read_fails_closed(tmp_path):
    items = case(tmp_path)
    source = items[3]
    original = source.get_provider_snapshot
    changed = replace(
        source.snapshot,
        revision=2,
        registrations=tuple(
            replace(entry, enabled=False) if entry.role == "DOCUMENT" else entry
            for entry in source.snapshot.registrations
        ),
    )
    def revoked(*args):
        current = original(*args)
        return changed if source.calls >= 4 else current
    source.get_provider_snapshot = revoked
    with pytest.raises(OnboardingError, match="ONBOARDING_STALE_OR_REVOKED_REVISION"):
        review(items)
    assert source.calls >= 4
    assert items[4]["IDENTITY"].client.calls == 1
    assert items[4]["REVIEW_PERMISSION"].client.calls == 0


def test_foreign_provider_registry_and_data_cannot_access_other_company(tmp_path):
    a = case(tmp_path, "EXTERNAL_COMPANY_A")
    b = case(tmp_path, "EXTERNAL_COMPANY_B")
    a[3] = b[3]
    with pytest.raises(OnboardingError, match="ONBOARDING_TENANT_MISMATCH"):
        review(a)
    assert a[4]["IDENTITY"].client.calls == 0


def test_changed_registration_source_or_provider_after_pin_is_denied(tmp_path):
    items = case(tmp_path)
    source = items[3]
    rows = list(source.snapshot.registrations)
    rows[1] = replace(rows[1], integration_ref="SYNTHETIC_DIFFERENT_SOURCE")
    source.snapshot = replace(source.snapshot, registrations=tuple(rows))
    with pytest.raises(OnboardingError, match="ONBOARDING_REGISTRY_DIGEST_CHANGED"):
        review(items)
    assert items[4]["IDENTITY"].client.calls == 0


@pytest.mark.parametrize("change,code", (
    ({"role": "UNDECLARED"}, "UNKNOWN_PROVIDER_ROLE"),
    ({"api_version": "2.0.0"}, "UNSUPPORTED_PROVIDER_API_VERSION"),
    ({"assurance": "AUTHENTICATED_REAL"}, "REAL_AUTHENTICATION_CLAIM_NOT_SUPPORTED"),
    ({"enabled": 1}, "INVALID_PROVIDER_STATUS"),
    ({"valid_from": None}, "INVALID_ONBOARDING_TIME"),
))
def test_invalid_registration_contract_rejected_at_construction(tmp_path, change, code):
    items = case(tmp_path)
    provider = items[3].snapshot.registrations[0]
    with pytest.raises(OnboardingError, match=code):
        replace(provider, **change)


def test_duplicate_provider_roles_and_identifiers_or_incomplete_registry_rejected(tmp_path):
    items = case(tmp_path)
    snapshot = items[3].snapshot
    with pytest.raises(OnboardingError, match="INCOMPLETE_PROVIDER_REGISTRY"):
        replace(snapshot, registrations=snapshot.registrations[:2])
    with pytest.raises(OnboardingError, match="UNORDERED_DUPLICATE_OR_MISSING_PROVIDER_ROLE"):
        replace(snapshot, registrations=(
            snapshot.registrations[1], snapshot.registrations[0], snapshot.registrations[2],
        ))
    with pytest.raises(OnboardingError, match="NONINDEPENDENT_PROVIDER_IDENTIFIERS"):
        replace(snapshot, registrations=(
            snapshot.registrations[0],
            replace(snapshot.registrations[1], provider_id=snapshot.registrations[0].provider_id),
            snapshot.registrations[2],
        ))


def test_no_real_claims_can_enter_provider_purpose_or_registry_policy(tmp_path):
    items = case(tmp_path)
    snapshot = items[3].snapshot
    with pytest.raises(OnboardingError, match="PROVIDER_REGISTRY_OPERATIONAL_PROMOTION"):
        replace(snapshot, purpose="PRESENTED_OPERATIONAL")
    with pytest.raises(OnboardingError, match="PROVIDER_REGISTRY_OPERATIONAL_PROMOTION"):
        replace(snapshot, policy_version="OPERATIONAL")
    with pytest.raises(OnboardingError, match="UNSUPPORTED_PINNED_PURPOSE"):
        replace(items[2], purpose="PRODUCTION")


def test_permission_escalation_remains_blocked_by_existing_f63(tmp_path):
    items = case(tmp_path)
    current = items[4]["REVIEW_PERMISSION"].client
    current.value = replace(current.value, permission="AUTHORIZE_PURCHASE")
    with pytest.raises(DocumentaryBoundaryError, match="REVIEW_PERMISSION_SCOPE_MISMATCH"):
        review(items)


def test_registry_digest_has_deterministic_canonical_digest_and_not_a_signature(tmp_path):
    items = case(tmp_path)
    snapshot = items[3].snapshot
    digest = fingerprint_provider_snapshot(snapshot)
    assert digest == items[2].expected_digest
    assert len(digest) == 64
    assert fingerprint_provider_snapshot(snapshot) == digest
    assert fingerprint_provider_snapshot(replace(snapshot, revision=2)) != digest
