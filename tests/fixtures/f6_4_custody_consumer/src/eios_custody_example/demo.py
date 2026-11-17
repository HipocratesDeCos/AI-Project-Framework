"""F6.4 end-to-end demonstration: separate local custody for synthetic companies.

This demonstration runs with test-double IdP and permission services, NEVER
with real credentials, real documents, admission or operational authority.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from eios_evidence_boundary_example.demo import scenario
from eios_evidence_boundary_example.review import (
    DocumentaryBoundaryError, review_synthetic_boundary,
)

from .custody import (
    CustodyError, DocumentBinding, SyntheticCustodyVault,
    VaultDocumentProvider,
)


def _binding(request) -> DocumentBinding:
    return DocumentBinding(
        project_id=request.project_id,
        company_id=request.company_id,
        source_id=request.source_id,
        data_snapshot_id=request.data_snapshot_id,
        document_ref=request.document_ref,
        expected_document_sha256=request.expected_document_sha256,
    )


def run() -> dict[str, object]:
    root = Path.cwd() / "synthetic-custody"
    root.mkdir(exist_ok=False)
    vault = SyntheticCustodyVault(root)
    cases = []
    first = None
    for company in ("EXTERNAL_COMPANY_A", "EXTERNAL_COMPANY_B"):
        prepared, request, identity, document_double, permission = scenario(company)
        binding = _binding(request)
        vault.store_once(binding, document_double.value.content)
        provider = VaultDocumentProvider(vault, binding)
        receipt = review_synthetic_boundary(
            prepared=prepared, request=request,
            identity_source=identity, document_source=provider,
            permission_source=permission,
        )
        assert receipt.status == "SYNTHETIC_BOUNDARY_CHECKS_PASSED"
        assert receipt.real_company_authenticated is False
        assert receipt.real_document_authenticated is False
        assert receipt.real_human_authorized is False
        assert receipt.production_authorized is False
        assert receipt.decision_authority is False
        assert receipt.operational_path == "FORBIDDEN"
        assert vault.load_verified(binding).content == document_double.value.content
        assert identity.calls == 2 and permission.calls == 2
        cases.append(asdict(receipt))
        if first is None:
            first = binding

    assert len(list(root.glob("*.json"))) == 2
    assert len({case["company_id"] for case in cases}) == 2
    assert len({case["document_sha256"] for case in cases}) == 2
    # A record of tenant B cannot be read via tenant A's other scoped pin.
    try:
        vault.load_verified(DocumentBinding(
            project_id=first.project_id,
            company_id="EXTERNAL_COMPANY_B",
            source_id=first.source_id,
            data_snapshot_id=first.data_snapshot_id,
            document_ref=first.document_ref,
            expected_document_sha256=first.expected_document_sha256,
        ))
    except CustodyError:
        pass
    else:
        raise AssertionError("Cross-tenant pin unexpectedly loaded data")

    return {
        "verification": "F6_4_EXTERNAL_CUSTODY_ISOLATED_SYNTHETIC_PASS",
        "company_count": len(cases),
        "immutable_record_count": len(list(root.glob("*.json"))),
        "receipts": cases,
        "identity_provider": "SYNTHETIC_TEST_DOUBLE",
        "permission_provider": "SYNTHETIC_TEST_DOUBLE",
        "document_origin_authenticity": "NOT_TESTED",
        "storage_security": "HOST_RESPONSIBILITY_NOT_CERTIFIED",
        "production_authorized": False,
        "operational_path": "FORBIDDEN",
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
