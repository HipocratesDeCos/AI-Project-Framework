"""F6.3 — adversarial proof that source integrity does not equal trust."""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests/fixtures/f6_2_external_company_adapter/src"))
sys.path.insert(0, str(ROOT / "tests/fixtures/f6_3_documentary_boundary_consumer/src"))

from eios_evidence_boundary_example import (  # noqa: E402
    DocumentaryBoundaryError, ReviewRequest, review_synthetic_boundary,
)
from eios_evidence_boundary_example.demo import run, scenario  # noqa: E402


def check(item):
    return review_synthetic_boundary(
        prepared=item[0], request=item[1],
        identity_source=item[2], document_source=item[3],
        permission_source=item[4],
    )


def fail(item, match):
    with pytest.raises(DocumentaryBoundaryError, match=match):
        check(item)


def test_two_companies_remain_synthetic_even_with_all_three_provider_responses():
    result = run()
    assert result["verification"] == "F6_3_SYNTHETIC_EXTERNAL_TRUST_BOUNDARY_PASS"
    assert result["production_authorized"] is False
    assert result["operational_path"] == "FORBIDDEN"
    assert result["real_enterprise_identity"] == "NOT_TESTED"
    assert result["real_document_authentication"] == "NOT_TESTED"
    assert result["real_human_review"] == "NOT_TESTED"
    assert len(result["receipts"]) == 2
    assert {x["company_id"] for x in result["receipts"]} == {
        "EXTERNAL_COMPANY_A", "EXTERNAL_COMPANY_B",
    }
    assert len({x["document_sha256"] for x in result["receipts"]}) == 2
    assert all(x["technical_input_validated"] for x in result["receipts"])
    for receipt in result["receipts"]:
        for field in ("real_company_authenticated", "real_document_authenticated",
                      "real_human_authorized", "production_authorized", "decision_authority"):
            assert receipt[field] is False
        assert receipt["provenance_status"] == "UNVERIFIED_ADAPTER_RESPONSIBILITY"


@pytest.mark.parametrize("position,method", (
    (2, "IDENTITY_PROVIDER_REQUIRED"),
    (3, "DOCUMENT_PROVIDER_REQUIRED"),
    (4, "PERMISSION_PROVIDER_REQUIRED"),
))
def test_absent_providers_are_rejected_before_any_external_call(position, method):
    items = list(scenario("EXTERNAL_COMPANY_A"))
    items[position] = None
    fail(items, method)
    assert all(x.calls == 0 for x in items[2:] if x is not None)


@pytest.mark.parametrize("field", (
    "project_id", "company_id", "source_id", "data_snapshot_id",
    "expected_source_sha256", "document_ref",
))
def test_cross_scope_or_modified_source_blocked_before_provider_calls(field):
    items = list(scenario("EXTERNAL_COMPANY_A"))
    value = "0" * 64 if field == "expected_source_sha256" else "FOREIGN"
    items[1] = items[1].model_copy(update={field: value})
    fail(items, "PREPARED_EXTERNAL_SCOPE_MISMATCH")
    assert all(provider.calls == 0 for provider in items[2:])


@pytest.mark.parametrize("field,value", (
    ("production_authorized", True),
    ("operational_path", "OPERATIONAL"),
    ("provenance_status", "DOCUMENT_AUTHENTICATED"),
))
def test_forged_technical_prepared_case_never_gains_operational_authority(field, value):
    items = list(scenario("EXTERNAL_COMPANY_A"))
    items[0] = replace(items[0], **{field: value})
    fail(items, "UNTRUSTED_PROVENANCE_PROMOTION")
    assert all(provider.calls == 0 for provider in items[2:])


@pytest.mark.parametrize("position,field,value,match", (
    (2, "project_id", "ANOTHER_PROJECT", "IDENTITY_SCOPE_MISMATCH"),
    (2, "company_id", "OTHER_COMPANY", "IDENTITY_SCOPE_MISMATCH"),
    (2, "session_ref", "OTHER_SESSION", "IDENTITY_SCOPE_MISMATCH"),
    (2, "subject_id", "", "INVALID_TRUST_FIELD"),
    (2, "identity_ref", "", "INVALID_TRUST_FIELD"),
    (2, "assurance", "CLAIMED_REAL_IDENTITY", "IDENTITY_NOT_IN_SYNTHETIC_SCOPE"),
    (3, "project_id", "OTHER_PROJECT", "DOCUMENT_SCOPE_MISMATCH"),
    (3, "company_id", "OTHER_COMPANY", "DOCUMENT_SCOPE_MISMATCH"),
    (3, "source_id", "FOREIGN_SOURCE", "DOCUMENT_SCOPE_MISMATCH"),
    (3, "data_snapshot_id", "OLDER_SNAPSHOT", "DOCUMENT_SCOPE_MISMATCH"),
    (3, "document_ref", "OTHER_DOCUMENT", "DOCUMENT_SCOPE_MISMATCH"),
    (3, "content", b"CHANGED_BYTES", "DOCUMENT_DIGEST_MISMATCH"),
    (3, "assurance", "CLAIMED_REAL_DOCUMENT", "DOCUMENT_NOT_IN_SYNTHETIC_SCOPE"),
    (4, "project_id", "OTHER_PROJECT", "REVIEW_PERMISSION_SCOPE_MISMATCH"),
    (4, "company_id", "OTHER_COMPANY", "REVIEW_PERMISSION_SCOPE_MISMATCH"),
    (4, "subject_id", "OTHER_REVIEWER", "REVIEW_PERMISSION_SCOPE_MISMATCH"),
    (4, "document_ref", "OTHER_DOCUMENT", "REVIEW_PERMISSION_SCOPE_MISMATCH"),
    (4, "permission", "AUTHORIZE_PURCHASE", "REVIEW_PERMISSION_SCOPE_MISMATCH"),
    (4, "grant_ref", "", "INVALID_TRUST_FIELD"),
    (4, "assurance", "CLAIMED_REAL_GRANT", "REVIEW_PERMISSION_NOT_IN_SYNTHETIC_SCOPE"),
))
def test_foreign_unverified_and_forged_provider_results_are_denied(
    position, field, value, match,
):
    items = list(scenario("EXTERNAL_COMPANY_A"))
    provider = items[position]
    provider.value = replace(provider.value, **{field: value})
    fail(items, match)


@pytest.mark.parametrize("position", (2, 4))
def test_expired_identity_or_permission_is_denied(position):
    items = list(scenario("EXTERNAL_COMPANY_A"))
    provider = items[position]
    provider.value = replace(
        provider.value,
        valid_to=items[1].reviewed_at - timedelta(seconds=1),
    )
    fail(items, "TRUST_WINDOW_NOT_VALID")


@pytest.mark.parametrize("position", (2, 3, 4))
def test_external_provider_revocation_or_document_change_between_checks_is_denied(position):
    items = list(scenario("EXTERNAL_COMPANY_A"))
    source = items[position]
    initial = source.value
    if position == 2:
        later = replace(initial, identity_ref="REVOKED_IDENTITY")
    elif position == 3:
        later = replace(initial, content=b"DIFFERENT", document_sha256="0" * 64)
    else:
        later = replace(initial, grant_ref="REVOKED_GRANT")
    method_name = ("resolve_identity", "load_document", "resolve_permission")[position - 2]
    original = getattr(source, method_name)
    def changed(*args):
        response = original(*args)
        if source.calls == 2:
            return later
        return response
    setattr(source, method_name, changed)
    if position == 3:
        fail(items, "DOCUMENT_DIGEST_MISMATCH")
    else:
        fail(items, "SYNTHETIC_TRUST_STATE_CHANGED")


def test_mismatched_expected_document_hash_rejected_despite_same_tenant():
    items = list(scenario("EXTERNAL_COMPANY_A"))
    items[1] = items[1].model_copy(update={"expected_document_sha256": "0" * 64})
    fail(items, "DOCUMENT_DIGEST_MISMATCH")


@pytest.mark.parametrize("modification", (
    {"purpose": "PRESENTED_OPERATIONAL"},
    {"document_ref": ""},
    {"reviewed_at": "2026-11-17T12:00:00"},
    {"project_id": ""},
    {"company_id": ""},
    {"real_company_authenticated": True},
))
def test_caller_request_cannot_inject_operational_trust_or_invalid_fields(modification):
    request = scenario("EXTERNAL_COMPANY_A")[1]
    with pytest.raises(ValidationError):
        ReviewRequest.model_validate({**request.model_dump(), **modification})


def test_same_company_success_performs_double_read_and_never_promotes_trust():
    items = scenario("EXTERNAL_COMPANY_A")
    receipt = check(items)
    assert receipt.status == "SYNTHETIC_BOUNDARY_CHECKS_PASSED"
    assert receipt.operational_path == "FORBIDDEN"
    assert receipt.decision_authority is False
    assert (items[2].calls, items[3].calls, items[4].calls) == (2, 2, 2)
