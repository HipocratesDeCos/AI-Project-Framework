"""F6.3 independent cross-company *synthetic* evidence/permission test doubles."""
from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json

from eios_company_adapter_example.demo import _prepare, _record

from .review import (
    DocumentaryBoundaryError, DocumentRecord, IdentityRecord,
    PermissionRecord, ReviewRequest, PERMISSION, review_synthetic_boundary,
)


class IdentityDouble:
    def __init__(self, value):
        self.value = value
        self.calls = 0

    def resolve_identity(self, session_ref, checked_at):
        self.calls += 1
        return self.value


class DocumentDouble:
    def __init__(self, value):
        self.value = value
        self.calls = 0

    def load_document(self, project_id, company_id, document_ref, checked_at):
        self.calls += 1
        return self.value


class PermissionDouble:
    def __init__(self, value):
        self.value = value
        self.calls = 0

    def resolve_permission(self, project_id, company_id, subject_id, document_ref, checked_at):
        self.calls += 1
        return self.value


def scenario(company: str):
    """Build two wholly independent synthetic company review contexts."""
    if company not in ("EXTERNAL_COMPANY_A", "EXTERNAL_COMPANY_B"):
        raise ValueError("Only predefined test companies can enter F6.3")
    payload = _record(company)
    prepared = _prepare(payload, [])
    now = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)
    session = "SYNTHETIC_SESSION_" + company
    document = ("SYNTHETIC_INSPECTION_RECEIPT|" + company).encode("utf-8")
    digest = sha256(document).hexdigest()
    request = ReviewRequest(
        session_ref=session,
        project_id=prepared.context.project_id,
        company_id=company,
        source_id=prepared.source_id,
        data_snapshot_id=prepared.context.data_snapshot_id,
        expected_source_sha256=prepared.raw_sha256,
        document_ref=prepared.operation.payload.inspection_reference,
        expected_document_sha256=digest,
        reviewed_at=now,
        purpose="SYNTHETIC_TEST_ONLY",
    )
    identity = IdentityDouble(IdentityRecord(
        project_id=request.project_id,
        company_id=company,
        session_ref=session,
        subject_id="SYNTHETIC_REVIEWER_" + company,
        identity_ref="SYNTHETIC_IDENTITY_" + company,
        valid_from=now - timedelta(minutes=10),
        valid_to=now + timedelta(minutes=10),
    ))
    evidence = DocumentDouble(DocumentRecord(
        project_id=request.project_id,
        company_id=company,
        source_id=request.source_id,
        data_snapshot_id=request.data_snapshot_id,
        document_ref=request.document_ref,
        document_sha256=digest,
        content=document,
    ))
    permission = PermissionDouble(PermissionRecord(
        project_id=request.project_id,
        company_id=company,
        subject_id=identity.value.subject_id,
        document_ref=request.document_ref,
        permission=PERMISSION,
        grant_ref="SYNTHETIC_GRANT_" + company,
        valid_from=now - timedelta(minutes=10),
        valid_to=now + timedelta(minutes=10),
    ))
    return prepared, request, identity, evidence, permission


def run() -> dict:
    receipts = []
    for company in ("EXTERNAL_COMPANY_A", "EXTERNAL_COMPANY_B"):
        inputs = scenario(company)
        receipt = review_synthetic_boundary(
            prepared=inputs[0], request=inputs[1],
            identity_source=inputs[2], document_source=inputs[3],
            permission_source=inputs[4],
        )
        assert receipt.status == "SYNTHETIC_BOUNDARY_CHECKS_PASSED"
        assert receipt.operational_path == "FORBIDDEN"
        assert receipt.real_company_authenticated is False
        assert receipt.real_document_authenticated is False
        assert receipt.real_human_authorized is False
        assert receipt.decision_authority is False
        assert (inputs[2].calls, inputs[3].calls, inputs[4].calls) == (2, 2, 2)
        receipts.append(asdict(receipt))

    # A correctly hashed record is NOT enough to cross a tenant boundary.
    b = scenario("EXTERNAL_COMPANY_B")
    a = scenario("EXTERNAL_COMPANY_A")
    try:
        review_synthetic_boundary(
            prepared=a[0], request=a[1],
            identity_source=b[2], document_source=b[3], permission_source=b[4],
        )
    except DocumentaryBoundaryError as exc:
        assert "IDENTITY_SCOPE_MISMATCH" in str(exc)
    else:
        raise AssertionError("Another company bypassed the identity boundary")
    assert len({record["company_id"] for record in receipts}) == 2
    return {
        "verification": "F6_3_SYNTHETIC_EXTERNAL_TRUST_BOUNDARY_PASS",
        "receipts": receipts,
        "real_enterprise_identity": "NOT_TESTED",
        "real_document_authentication": "NOT_TESTED",
        "real_human_review": "NOT_TESTED",
        "proof_sources": "SYNTHETIC_TEST_DOUBLES_ONLY",
        "production_authorized": False,
        "operational_path": "FORBIDDEN",
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
