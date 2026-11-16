"""F3.6: adversarial whole-chain conformance, not a simulated corporate login.

Use the EXISTING F3.5 entry point and F2.4/F3.3/F3.4 synthetic fixtures.
No duplicate parameter centre, identity or trust provider is introduced here.
"""
from dataclasses import replace
from datetime import timedelta

import pytest

from eios.parameters.company_identity_gate import (
    read_authenticated_company_parameter_selection,
)
from eios.parameters.key_lifecycle import (
    IndependentLifecycleCheckpoint,
)
from eios.parameters.version_binding import ParameterVersionBindingError
from test_company_identity_gate import fixture
from test_key_lifecycle import bind_history, event, set_history, COMPANY_A, COMPANY_B, WHEN


def check_failure(case, code):
    with pytest.raises(ParameterVersionBindingError) as err:
        read_authenticated_company_parameter_selection(**case)
    assert err.value.code == code


def test_complete_chain_produces_no_decision_authority():
    case, ids, grants, roots, records, history, checkpoint, *_ = fixture()
    receipt = read_authenticated_company_parameter_selection(**case)
    assert receipt.company_id == COMPANY_A
    assert receipt.selection.manifest.company_id == COMPANY_A
    assert receipt.selection.manifest.parameters_version == case["context"].parameters_version
    assert receipt.selection.lookup.complete_documentary_coverage
    assert receipt.selection.source_authentication == "ADAPTER_RESPONSIBILITY"
    assert receipt.authentication_boundary == "EXTERNAL_PROVIDER_RESPONSIBILITY"
    assert receipt.operational_path == "FORBIDDEN"
    assert receipt.decision_authority is False
    assert receipt.selection.operational_path == "FORBIDDEN"
    assert receipt.selection.decision_authority is False


def test_unauthenticated_company_cannot_reuse_another_company_verified_documents():
    alpha, *_ = fixture(company=COMPANY_A)
    beta, ids, grants, roots, records, history, checkpoint, *_ = fixture(company=COMPANY_B)
    # A caller provides parameters/evidence from another company while the
    # independently verified session belongs to B: no fallback to A.
    beta["center"] = alpha["center"]
    beta["evidence_by_parameter"] = alpha["evidence_by_parameter"]
    with pytest.raises((ParameterVersionBindingError, ValueError)) as err:
        read_authenticated_company_parameter_selection(**beta)
    assert not isinstance(err.value, TypeError)


def test_wrong_tenant_manifest_under_valid_company_governance_is_denied():
    alpha, _ids_a, _grants_a, _roots_a, records_a, *_ = fixture(company=COMPANY_A)
    beta, ids, grants, roots, records, history, checkpoint, *_ = fixture(company=COMPANY_B)
    # F3.3 must validate the signature against B's key; the A record cannot
    # be relabelled by an authenticated B session.
    records.records[0] = records_a.records[0]
    check_failure(beta, "SIGNATURE_INVALID")


def test_foreign_governance_root_and_checkpoint_cannot_be_imported_from_a():
    alpha, *_prefix_a, root_a, trust_a, state_a = fixture(company=COMPANY_A)
    beta, ids, grants, roots, records, history, checkpoint, *_ = fixture(company=COMPANY_B)
    roots.root = root_a
    check_failure(beta, "COMPANY_TRUST_SCOPE_MISMATCH")


def test_revoked_key_during_first_signed_manifest_read_fails_before_return():
    case, ids, grants, roots, records, history, checkpoint, gov, root, trust, state = fixture()

    class RevokingRecordRepository:
        triggered = False
        def get_signed_record(self, company_id, version, effective_at):
            if not self.triggered:
                self.triggered = True
                state["events"].append(event(
                    3, "REVOKE", trust.key_id, WHEN - timedelta(hours=1),
                    approval_ref="SYNTHETIC-REVOKE-WHILE-READING",
                ))
                state["revision"] = len(state["events"])
                set_history(gov, history, checkpoint, state)
            return records.records[0]

    case["record_repository"] = RevokingRecordRepository()
    check_failure(case, "KEY_REVOKED")


def test_revocation_between_f24_manifest_reads_fails_instead_of_returning_old_selection():
    case, ids, grants, roots, records, history, checkpoint, gov, root, trust, state = fixture()

    class RevokingCheckpoint:
        calls = 0
        def get_checkpoint(self, company_id, issuer_id):
            self.calls += 1
            if self.calls == 3:
                # F3.4 performs two checkpoint reads per manifest; the third
                # is the next F2.4 version-source read, after Centre lookup.
                state["events"].append(event(
                    3, "REVOKE", trust.key_id, WHEN - timedelta(hours=1),
                    approval_ref="SYNTHETIC-REVOKE-BETWEEN-MANIFESTS",
                ))
                state["revision"] = len(state["events"])
                set_history(gov, history, checkpoint, state)
            return checkpoint.checkpoint

    case["checkpoint_source"] = RevokingCheckpoint()
    check_failure(case, "KEY_REVOKED")


def test_loss_of_identity_after_f24_selection_rejects_successful_manifest_checks():
    case, ids, grants, roots, records, history, checkpoint, *_ = fixture()

    class RevokedSession:
        calls = 0
        def resolve_authenticated_identity(self, session_ref, at):
            self.calls += 1
            return ids.identity if self.calls == 1 else None

    case["identity_source"] = RevokedSession()
    check_failure(case, "IDENTITY_UNVERIFIED")
    assert len(records.calls) == 2


def test_loss_of_grant_after_f24_selection_rejects_successful_manifest_checks():
    case, ids, grants, roots, records, history, checkpoint, *_ = fixture()

    class RevokedGrant:
        calls = 0
        def resolve_parameter_read_grant(self, company_id, subject_id, at):
            self.calls += 1
            return grants.grant if self.calls == 1 else None

    case["authorization_source"] = RevokedGrant()
    check_failure(case, "COMPANY_GRANT_MISSING")
    assert len(records.calls) == 2


def test_new_version_under_valid_session_without_signed_historical_record_is_denied():
    case, ids, grants, roots, records, history, checkpoint, *_ = fixture()
    case["context"] = case["context"].model_copy(
        update={"parameters_version": "UNSIGNED-OTHER-VERSION"}
    )
    check_failure(case, "SIGNED_SCOPE_MISMATCH")


def test_missing_documentary_proof_not_replaced_by_corporate_identity():
    case, *_ = fixture()
    case["evidence_by_parameter"] = {}
    check_failure(case, "INCOMPLETE_DOCUMENTARY_COVERAGE")


def test_valid_signature_but_wrong_parameter_configuration_is_denied():
    case, ids, grants, roots, records, history, checkpoint, *_ = fixture()
    center_repo = case["center"]._repository
    center_repo.configs[0] = replace(center_repo.configs[0], value="No")
    check_failure(case, "VERSION_CONTENT_MISMATCH")


def test_unavailable_external_checkpoint_never_falls_back_to_signed_history():
    case, ids, grants, roots, records, history, checkpoint, *_ = fixture()
    checkpoint.checkpoint = None
    check_failure(case, "CHECKPOINT_UNAVAILABLE")
    assert not records.calls


def test_attacker_cannot_replay_pre_revocation_history_even_with_original_valid_signature():
    case, ids, grants, roots, records, history, checkpoint, gov, root, trust, state = fixture()
    previous = history.record
    state["events"].append(event(
        3, "REVOKE", trust.key_id, WHEN - timedelta(hours=1),
        approval_ref="SYNTHETIC-REVOKE-ANTIREPLAY",
    ))
    state["revision"] = len(state["events"])
    set_history(gov, history, checkpoint, state)
    history.record = previous
    check_failure(case, "CHECKPOINT_MISMATCH")
    assert not records.calls


def test_trusted_root_replacement_between_session_checks_rejected_without_granting_authority():
    case, ids, grants, roots, records, history, checkpoint, *_ = fixture()
    roots.after_first = replace(
        roots.root, governance_key_id="DIFFERENT-ROOT",
    )
    check_failure(case, "COMPANY_AUTHORIZATION_CHANGED")


def test_issuer_approval_reference_does_not_authorize_operational_purchase():
    case, ids, grants, roots, records, history, checkpoint, *_ = fixture()
    receipt = read_authenticated_company_parameter_selection(**case)
    assert receipt.grant_ref.startswith("TEST-")
    assert receipt.selection.manifest.source_ref.startswith("synthetic-")
    assert receipt.decision_authority is False
    assert receipt.operational_path == "FORBIDDEN"


def test_missing_root_source_never_uses_key_from_client_manifest():
    case, ids, grants, roots, records, history, checkpoint, *_ = fixture()
    case["root_source"] = None
    check_failure(case, "COMPANY_TRUST_SOURCE_MISSING")
    assert not records.calls


def test_expired_grant_fails_even_if_current_manifest_signature_is_valid():
    case, ids, grants, roots, records, history, checkpoint, *_ = fixture()
    grants.grant = replace(
        grants.grant,
        valid_to=WHEN - timedelta(seconds=1),
    )
    check_failure(case, "IDENTITY_OR_PERMISSION_EXPIRED")
    assert not records.calls
