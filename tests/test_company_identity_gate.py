"""F3.5: host-attested company scope, grants and existing F3.4/F2.4 boundary.

These are SYNTHETIC host providers. They do not establish an actual corporate
identity, permissions service, key management account or operational admission.
"""
from dataclasses import replace
from datetime import timedelta

import pytest

from eios.parameters.company_identity_gate import (
    READ_PERMISSION, AuthenticatedCompanyIdentity, CompanyIssuerReadGrant,
    read_authenticated_company_parameter_selection,
)
from eios.parameters.version_binding import ParameterVersionBindingError
from test_key_lifecycle import (
    sample as governance_sample,
    event, set_history, COMPANY_A, COMPANY_B, WHEN,
)


class IdentitySource:
    def __init__(self, identity):
        self.identity = identity
        self.calls = []
        self.after_first = None

    def resolve_authenticated_identity(self, session_ref, verification_at):
        self.calls.append((session_ref, verification_at))
        if self.after_first is not None and len(self.calls) > 1:
            return self.after_first
        return self.identity


class AuthorizationSource:
    def __init__(self, grant):
        self.grant = grant
        self.calls = []
        self.after_first = None

    def resolve_parameter_read_grant(self, company_id, subject_id, verification_at):
        self.calls.append((company_id, subject_id, verification_at))
        if self.after_first is not None and len(self.calls) > 1:
            return self.after_first
        return self.grant


class RootSource:
    def __init__(self, root):
        self.root = root
        self.calls = []
        self.after_first = None

    def get_trusted_governance_key(self, company_id, verification_at):
        self.calls.append((company_id, verification_at))
        if self.after_first is not None and len(self.calls) > 1:
            return self.after_first
        return self.root


def fixture(*, company=COMPANY_A):
    args, records, _, issuer, payload, issuer_trust, governor, root, history, checkpoint, state = governance_sample(
        company=company,
    )
    identity = AuthenticatedCompanyIdentity(
        company_id=company, subject_id="AUTHENTICATED-TEST-SUBJECT",
        identity_provider_id="SYNTHETIC-TEST-IDP", identity_ref="TEST-SESSION-001",
        valid_from=WHEN - timedelta(days=2),
        valid_to=WHEN + timedelta(days=2),
    )
    grant = CompanyIssuerReadGrant(
        company_id=company, subject_id=identity.subject_id,
        permission=READ_PERMISSION, issuer_id=issuer_trust.issuer_id,
        key_id=issuer_trust.key_id, grant_ref="TEST-ACCESS-GRANT-001",
        valid_from=WHEN - timedelta(days=2),
        valid_to=WHEN + timedelta(days=2),
    )
    id_source = IdentitySource(identity)
    grant_source = AuthorizationSource(grant)
    root_source = RootSource(root)
    kwargs = dict(
        session_ref="OPAQUE-SYNTHETIC-TEST-SESSION",
        requested_company_id=company,
        identity_source=id_source, authorization_source=grant_source,
        root_source=root_source, history_repository=history,
        checkpoint_source=checkpoint, record_repository=records,
        center=args["center"], context=args["context"],
        effective_at=args["effective_at"],
        verification_at=WHEN, parameter_ids=args["parameter_ids"],
        evidence_by_parameter=args["evidence_by_parameter"],
    )
    return kwargs, id_source, grant_source, root_source, records, history, checkpoint, governor, root, issuer_trust, state


def read(kwargs):
    return read_authenticated_company_parameter_selection(**kwargs)


def assert_failed(code, kwargs):
    with pytest.raises(ParameterVersionBindingError) as raised:
        read(kwargs)
    assert raised.value.code == code


def test_authorized_test_company_reuses_signed_governance_and_complete_f24_selection():
    args, ids, grants, roots, records, history, checkpoint, *_ = fixture()
    receipt = read(args)
    assert receipt.status == "HOST_IDENTITY_GRANT_AND_VERSION_MATCHED"
    assert receipt.company_id == COMPANY_A
    assert receipt.subject_id == "AUTHENTICATED-TEST-SUBJECT"
    assert receipt.identity_ref == "TEST-SESSION-001"
    assert receipt.grant_ref == "TEST-ACCESS-GRANT-001"
    assert receipt.selection.lookup.complete_documentary_coverage
    assert receipt.selection.manifest.company_id == COMPANY_A
    assert receipt.selection.manifest.selection_fingerprint == receipt.selection.selection_fingerprint
    assert receipt.authentication_boundary == "EXTERNAL_PROVIDER_RESPONSIBILITY"
    assert receipt.decision_authority is False
    assert receipt.operational_path == "FORBIDDEN"
    assert receipt.selection.decision_authority is False
    assert receipt.selection.operational_path == "FORBIDDEN"
    assert len(ids.calls) == len(grants.calls) == len(roots.calls) == 2
    assert history.calls == checkpoint.calls == 4
    assert len(records.calls) == 2


def test_absent_external_authenticated_session_denies_without_source_reads():
    args, ids, grants, roots, records, *_ = fixture()
    ids.identity = None
    assert_failed("IDENTITY_UNVERIFIED", args)
    assert not grants.calls and not roots.calls and not records.calls


def test_arbitrary_session_ref_not_authenticated_by_idp_is_denied():
    args, ids, grants, roots, records, *_ = fixture()
    args["session_ref"] = "user-supplied-pretend-auth-token"
    ids.identity = None
    assert_failed("IDENTITY_UNVERIFIED", args)
    assert not records.calls


def test_requested_other_company_never_overrides_authenticated_tenant():
    args, ids, grants, roots, records, *_ = fixture()
    args["requested_company_id"] = COMPANY_B
    assert_failed("IDENTITY_COMPANY_MISMATCH", args)
    assert not grants.calls and not records.calls


def test_missing_permission_denies_after_identity_before_governance():
    args, ids, grants, roots, records, *_ = fixture()
    grants.grant = None
    assert_failed("COMPANY_GRANT_MISSING", args)
    assert not roots.calls and not records.calls


@pytest.mark.parametrize("field,value,code", [
    ("company_id", COMPANY_B, "COMPANY_GRANT_SCOPE_MISMATCH"),
    ("subject_id", "ANOTHER-USER", "COMPANY_GRANT_SCOPE_MISMATCH"),
    ("permission", "PARAMETER_VERSION_WRITE", "COMPANY_PERMISSION_DENIED"),
    ("grant_ref", "", "INVALID_IDENTITY_SCOPE"),
])
def test_self_declared_wrong_tenant_principal_permission_or_reference_fails(field, value, code):
    args, ids, grants, roots, records, *_ = fixture()
    grants.grant = replace(grants.grant, **{field: value})
    assert_failed(code, args)
    assert not roots.calls and not records.calls


def test_wrong_issuer_grant_cannot_select_key_from_other_governance():
    args, ids, grants, roots, records, *_ = fixture()
    grants.grant = replace(grants.grant, issuer_id="OTHER-ISSUER")
    assert_failed("CHECKPOINT_SCOPE_MISMATCH", args)
    assert not records.calls


def test_wrong_key_grant_cannot_reuse_signature_of_existing_authorized_key():
    args, ids, grants, roots, records, *_ = fixture()
    grants.grant = replace(grants.grant, key_id="OTHER-KEY")
    assert_failed("KEY_NOT_ENROLLED", args)
    assert not records.calls


def test_trust_root_for_another_company_rejected():
    args, ids, grants, roots, records, *_ = fixture()
    roots.root = replace(roots.root, company_id=COMPANY_B)
    assert_failed("COMPANY_TRUST_SCOPE_MISMATCH", args)
    assert not records.calls


@pytest.mark.parametrize("missing,code", [
    ("identity_source", "IDENTITY_SOURCE_MISSING"),
    ("authorization_source", "AUTHORIZATION_SOURCE_MISSING"),
    ("root_source", "COMPANY_TRUST_SOURCE_MISSING"),
])
def test_missing_host_service_fails_closed_before_reading_documents(missing, code):
    args, ids, grants, roots, records, *_ = fixture()
    args[missing] = None
    assert_failed(code, args)
    assert not records.calls


def test_expired_company_identity_and_grant_rejected():
    args, ids, grants, roots, records, *_ = fixture()
    ids.identity = replace(ids.identity, valid_to=WHEN)
    assert_failed("IDENTITY_OR_PERMISSION_EXPIRED", args)
    assert not records.calls
    ids.identity = replace(ids.identity, valid_to=WHEN + timedelta(days=1))
    grants.grant = replace(grants.grant, valid_to=WHEN)
    assert_failed("IDENTITY_OR_PERMISSION_EXPIRED", args)
    assert not records.calls


def test_naive_clock_and_invalid_identity_windows_fail_closed():
    args, ids, grants, roots, records, *_ = fixture()
    args["verification_at"] = WHEN.replace(tzinfo=None)
    assert_failed("INVALID_IDENTITY_WINDOW", args)
    ids.identity = replace(ids.identity, valid_from=WHEN + timedelta(days=1))
    args["verification_at"] = WHEN
    assert_failed("IDENTITY_OR_PERMISSION_EXPIRED", args)
    assert not records.calls


def test_role_or_identity_revision_change_during_selection_rejected():
    args, ids, grants, roots, records, *_ = fixture()
    grants.after_first = replace(grants.grant, grant_ref="REVOKED-REPLACED-GRANT")
    assert_failed("COMPANY_AUTHORIZATION_CHANGED", args)
    assert len(records.calls) == 2


def test_authenticated_identity_reference_change_during_selection_rejected():
    args, ids, grants, roots, records, *_ = fixture()
    ids.after_first = replace(ids.identity, identity_ref="SESSION-CHANGED-DURING-READ")
    assert_failed("COMPANY_AUTHORIZATION_CHANGED", args)
    assert len(records.calls) == 2


def test_governance_root_drift_during_selection_rejected():
    args, ids, grants, roots, records, *_ = fixture()
    roots.after_first = replace(
        roots.root, governance_key_id="NEW-ROOT-MUST-BE-REVALIDATED",
    )
    assert_failed("COMPANY_AUTHORIZATION_CHANGED", args)
    assert len(records.calls) == 2


def test_revoked_key_still_denied_with_valid_identity_and_grant():
    args, ids, grants, roots, records, history, checkpoint, governor, root, trust, state = fixture()
    state["events"].append(event(
        3, "REVOKE", trust.key_id, WHEN - timedelta(hours=2),
        approval_ref="TEST-REVOCATION-001",
    ))
    state["revision"] = len(state["events"])
    set_history(governor, history, checkpoint, state)
    assert_failed("KEY_REVOKED", args)
    assert not records.calls


def test_company_identity_and_grant_cannot_substitute_missing_c0_documentary_evidence():
    args, ids, grants, roots, records, *_ = fixture()
    args["evidence_by_parameter"] = {}
    assert_failed("INCOMPLETE_DOCUMENTARY_COVERAGE", args)
    assert len(records.calls) == 1


def test_identity_and_key_valid_but_live_config_changed_still_rejected():
    args, ids, grants, roots, records, *_ = fixture()
    center_repo = args["center"]._repository
    center_repo.configs[0] = replace(center_repo.configs[0], value="No")
    assert_failed("VERSION_CONTENT_MISMATCH", args)


def test_another_synthetic_company_requires_its_own_external_providers():
    args_a, *_ = fixture(company=COMPANY_A)
    args_b, *_ = fixture(company=COMPANY_B)
    a = read(args_a)
    b = read(args_b)
    assert a.company_id == COMPANY_A
    assert b.company_id == COMPANY_B
    assert a.selection.selection_fingerprint != b.selection.selection_fingerprint


def test_f35_does_not_implement_identity_or_key_creation_or_operational_admission():
    args, ids, grants, roots, records, *_ = fixture()
    result = read(args)
    assert result.decision_authority is False
    assert result.operational_path == "FORBIDDEN"
    assert not hasattr(ids, "issue_identity")
    assert not hasattr(grants, "grant_permission")
    assert not hasattr(roots, "register_company")
    assert not hasattr(result, "authorize_purchase")
