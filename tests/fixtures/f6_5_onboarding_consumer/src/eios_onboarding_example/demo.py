"""F6.5: synthetic two-company provider onboarding and end-to-end F6.3 review.

Each synthetic company has a distinct host-controlled pinned registry, three
independent provider IDs, one F6.4 custody document, one F6.2 prepared case.
An accepted result is NEVER a real authenticated company or operational grant.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import timedelta
import json
from pathlib import Path

from eios_evidence_boundary_example.demo import scenario
from eios_custody_example.custody import (
    SyntheticCustodyVault, VaultDocumentProvider,
)
from eios_custody_example.demo import _binding

from .onboarding import (
    API_VERSION, ROLES, OnboardingError, OnboardingSnapshot,
    PinnedOnboarding, ProviderEndpoint, ProviderRegistration,
    fingerprint_provider_snapshot, review_with_onboarded_providers,
)


class RegistryDouble:
    """An IN-MEMORY TEST DOUBLE, not a trusted enterprise provider registry."""

    def __init__(self, snapshot: OnboardingSnapshot):
        self.snapshot = snapshot
        self.calls = 0

    def get_provider_snapshot(self, project_id, company_id, at):
        self.calls += 1
        return self.snapshot


def fixture(company: str, root: Path):
    if company not in ("EXTERNAL_COMPANY_A", "EXTERNAL_COMPANY_B"):
        raise ValueError("Only predefined fake companies enter the onboarding demo")
    prepared, request, identity, document, permission = scenario(company)
    vault = SyntheticCustodyVault(root)
    binding = _binding(request)
    vault.store_once(binding, document.value.content)
    custody = VaultDocumentProvider(vault, binding)
    clients = {
        "IDENTITY": identity,
        "DOCUMENT": custody,
        "REVIEW_PERMISSION": permission,
    }
    registrations = tuple(
        ProviderRegistration(
            role=role,
            provider_id="SYNTH_" + role + "_" + company,
            project_id=request.project_id,
            company_id=request.company_id,
            integration_ref="SYNTHETIC_INTEGRATION_" + role,
            api_version=API_VERSION,
            valid_from=request.reviewed_at - timedelta(days=1),
            valid_to=request.reviewed_at + timedelta(days=1),
            enabled=True,
        )
        for role in ROLES
    )
    snapshot = OnboardingSnapshot(
        project_id=request.project_id,
        company_id=company,
        revision=1,
        registrations=registrations,
    )
    pin = PinnedOnboarding(
        project_id=request.project_id,
        company_id=company,
        expected_revision=snapshot.revision,
        expected_digest=fingerprint_provider_snapshot(snapshot),
    )
    endpoints = {
        role: ProviderEndpoint(
            provider_id=registration.provider_id,
            role=role, api_version=API_VERSION,
            client=clients[role],
        )
        for role, registration in zip(ROLES, registrations)
    }
    return prepared, request, pin, RegistryDouble(snapshot), endpoints


def run() -> dict:
    root = Path.cwd() / "synthetic-onboarding-custody"
    root.mkdir(exist_ok=False)
    receipts = []
    for company in ("EXTERNAL_COMPANY_A", "EXTERNAL_COMPANY_B"):
        prepared, request, pin, source, endpoints = fixture(company, root)
        receipt = review_with_onboarded_providers(
            prepared=prepared, request=request, pin=pin,
            registry_source=source, endpoints=endpoints,
        )
        assert receipt.status == "SYNTHETIC_PROVIDER_ONBOARDING_READY"
        assert receipt.real_provider_connected is False
        assert receipt.real_enterprise_authenticated is False
        assert receipt.real_document_authenticated is False
        assert receipt.real_reviewer_authorized is False
        assert receipt.production_authorized is False
        assert receipt.decision_authority is False
        assert receipt.operational_path == "FORBIDDEN"
        assert source.calls == 14  # initial + 12 (before/after x 6) + final
        assert endpoints["IDENTITY"].client.calls == 2
        assert endpoints["REVIEW_PERMISSION"].client.calls == 2
        receipts.append(asdict(receipt))
    assert len({r["company_id"] for r in receipts}) == 2
    assert len({r["registry_digest"] for r in receipts}) == 2
    assert len(list(root.glob("*.json"))) == 2
    return {
        "verification": "F6_5_PROVIDER_ONBOARDING_SYNTHETIC_ONLY_PASS",
        "companies": len(receipts),
        "registrations_per_company": 3,
        "receipts": receipts,
        "provider_connection": "TEST_DOUBLES_ONLY",
        "enterprise_identity_authentication": "NOT_TESTED",
        "documentary_authentication": "NOT_TESTED",
        "human_review_authorization": "NOT_TESTED",
        "production_authorized": False,
        "operational_path": "FORBIDDEN",
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
