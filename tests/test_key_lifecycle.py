"""F3.4: signed issuer-key lifecycle/independent checkpoint integration tests.

Test governance/issuer PRIVATE keys are generated in memory only. No real
company identity, approval, revocation service or credentials are provided.
"""
from dataclasses import replace
from datetime import timedelta
from hashlib import sha256
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from eios.parameters.key_lifecycle import (
    SCHEMA, GovernanceVerificationKey, SignedKeyLifecycleHistory,
    IndependentLifecycleCheckpoint, GovernedParameterVersionSource,
)
from eios.parameters.version_binding import (
    ParameterVersionBindingError, read_version_bound_parameter_selection,
)
from eios.parameters.signed_version_source import SignedParameterVersionRecord
from test_signed_parameter_version_source import (
    fixture as signed_fixture, _canonical, COMPANY_A, COMPANY_B, WHEN,
)


class HistoryRepo:
    def __init__(self, record):
        self.record = record
        self.calls = 0

    def get_signed_history(self, company_id, issuer_id):
        self.calls += 1
        return self.record


class CheckpointSource:
    def __init__(self, checkpoint):
        self.checkpoint = checkpoint
        self.calls = 0

    def get_checkpoint(self, company_id, issuer_id):
        self.calls += 1
        return self.checkpoint


def event(seq, action, key_id, at, *, approval_ref=None,
          public_key_hex=None, valid_from=None, valid_to=None):
    return dict(
        sequence=seq, action=action, key_id=key_id, at=at.isoformat(),
        approval_ref=approval_ref, public_key_hex=public_key_hex,
        valid_from=valid_from.isoformat() if valid_from else None,
        valid_to=valid_to.isoformat() if valid_to else None,
    )


def raw_public(private):
    return private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def enroll(key_id, key_public, at=WHEN - timedelta(days=12), end=WHEN + timedelta(days=20)):
    return event(
        1, "ENROLL", key_id, at,
        public_key_hex=key_public.hex(),
        valid_from=WHEN - timedelta(days=20), valid_to=end,
    )


def authorize(seq=2, key_id="SYNTHETIC-KEY-1", at=WHEN - timedelta(days=11)):
    return event(seq, "AUTHORIZE", key_id, at, approval_ref="APPROVAL-TEST-001")


def history_payload(events, company=COMPANY_A, issuer="TEST-CORPORATE-ISSUER",
                    issued=None, expires=None):
    return {
        "schema": SCHEMA, "company_id": company, "issuer_id": issuer,
        "governance_key_id": "TEST-GOVERNANCE-ROOT-1",
        "revision": len(events), "events": events,
        "issued_at": (issued or WHEN - timedelta(hours=1)).isoformat(),
        "expires_at": (expires or WHEN + timedelta(hours=24)).isoformat(),
    }


def bind_history(governance_private, payload):
    encoded = _canonical(payload)
    return SignedKeyLifecycleHistory(encoded, governance_private.sign(encoded))


def checkpoint_for(signed, payload):
    return IndependentLifecycleCheckpoint(
        company_id=payload["company_id"], issuer_id=payload["issuer_id"],
        revision=payload["revision"],
        payload_sha256=sha256(signed.payload).hexdigest(),
    )


def sample(*, company=COMPANY_A, events=None, issuer_private=None,
           history_company=None, governor=None):
    args, records, center, issuer_private, signed_payload, trust = signed_fixture(
        company=company,
    )
    governor = governor or Ed25519PrivateKey.generate()
    root = GovernanceVerificationKey(
        company_id=company, governance_key_id="TEST-GOVERNANCE-ROOT-1",
        public_key_bytes=raw_public(governor),
        valid_from=WHEN - timedelta(days=30),
        valid_to=WHEN + timedelta(days=30),
    )
    if events is None:
        events = [enroll(trust.key_id, trust.public_key_bytes),
                  authorize(key_id=trust.key_id)]
    payload = history_payload(events, company=history_company or company)
    signed = bind_history(governor, payload)
    stored_history = HistoryRepo(signed)
    stored_checkpoint = CheckpointSource(checkpoint_for(signed, payload))
    source = GovernedParameterVersionSource(
        company_id=company, issuer_id=trust.issuer_id, key_id=trust.key_id,
        governance_key=root, history_repository=stored_history,
        checkpoint_source=stored_checkpoint, record_repository=records,
        verification_at=WHEN,
    )
    args["version_source"] = source
    return args, records, center, issuer_private, signed_payload, trust, governor, root, stored_history, stored_checkpoint, payload


def fails(code, args):
    with pytest.raises(ParameterVersionBindingError) as exc:
        read_version_bound_parameter_selection(**args)
    assert exc.value.code == code


def set_history(governor, repo, checkpoint_source, payload, *, update_checkpoint=True):
    signed = bind_history(governor, payload)
    repo.record = signed
    if update_checkpoint:
        checkpoint_source.checkpoint = checkpoint_for(signed, payload)


def test_signed_governance_and_issuer_manifest_reuse_f24_without_business_authority():
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = sample()
    result = read_version_bound_parameter_selection(**args)
    assert result.manifest.company_id == COMPANY_A
    assert result.manifest.parameters_version == payload["parameters_version"]
    assert result.lookup.complete_documentary_coverage
    assert result.status == "SOURCE_MANIFEST_MATCHED"
    assert result.decision_authority is False
    assert result.operational_path == "FORBIDDEN"
    assert args["version_source"].source_authentication == "UNATTESTED_UNTIL_MANIFEST_RETURNED"
    assert args["version_source"].decision_authority is False
    # The F2.4 double read invokes governance twice for each manifest read.
    assert history.calls == checkpoint.calls == 4
    assert len(records.calls) == 2


def test_unapproved_enrolled_key_is_never_accepted():
    original = sample()
    event1 = original[-1]["events"][0]
    args, records, center, *_ = sample(events=[event1])
    fails("KEY_NOT_AUTHORIZED", args)
    assert center.calls == [(COMPANY_A, "P-PAG-004", WHEN)]
    assert not records.calls


def test_revoked_key_rejects_even_manifest_signed_before_revocation():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    state["events"].append(event(3, "REVOKE", trust.key_id,
                                 WHEN - timedelta(hours=2),
                                 approval_ref="APPROVAL-REVOKE-001"))
    state["revision"] = len(state["events"])
    set_history(gov, history, checkpoint, state)
    fails("KEY_REVOKED", args)
    assert not records.calls


def test_suspended_key_rejects_until_new_explicit_authorization():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    state["events"].append(event(3, "SUSPEND", trust.key_id,
                                 WHEN - timedelta(days=2),
                                 approval_ref="APPROVAL-SUSPEND"))
    state["revision"] = len(state["events"])
    set_history(gov, history, checkpoint, state)
    fails("KEY_NOT_AUTHORIZED", args)
    state["events"].append(event(4, "AUTHORIZE", trust.key_id,
                                 WHEN - timedelta(days=1),
                                 approval_ref="APPROVAL-RESUME"))
    state["revision"] = len(state["events"])
    set_history(gov, history, checkpoint, state)
    result = read_version_bound_parameter_selection(**args)
    assert result.lookup.complete_documentary_coverage


def test_renewal_extends_active_key_with_approval_and_keeps_old_key_bytes():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    state["events"].append(event(3, "RENEW", trust.key_id,
                                 WHEN - timedelta(days=2),
                                 valid_to=WHEN + timedelta(days=50),
                                 approval_ref="APPROVAL-RENEW"))
    state["revision"] = len(state["events"])
    set_history(gov, history, checkpoint, state)
    assert read_version_bound_parameter_selection(**args).manifest.company_id == COMPANY_A


def test_renewal_cannot_resurrect_revoked_key():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    state["events"].append(event(3, "REVOKE", trust.key_id,
                                 WHEN - timedelta(days=2),
                                 approval_ref="APPROVAL-REVOKE"))
    state["events"].append(event(4, "RENEW", trust.key_id,
                                 WHEN - timedelta(days=1),
                                 valid_to=WHEN + timedelta(days=50),
                                 approval_ref="APPROVAL-RENEW"))
    state["revision"] = len(state["events"])
    set_history(gov, history, checkpoint, state)
    fails("INVALID_LIFECYCLE_TRANSITION", args)


def test_revoked_key_id_cannot_be_reenrolled_with_new_key():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    state["events"].append(event(3, "REVOKE", trust.key_id,
                                 WHEN - timedelta(days=2),
                                 approval_ref="APPROVAL-REVOKE"))
    new = Ed25519PrivateKey.generate()
    e = enroll(trust.key_id, raw_public(new), at=WHEN - timedelta(days=1))
    e["sequence"] = 4
    state["events"].append(e)
    state["revision"] = len(state["events"])
    set_history(gov, history, checkpoint, state)
    fails("INVALID_LIFECYCLE_TRANSITION", args)


def test_rollback_to_pre_revocation_history_fails_against_checkpoint():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    old = history.record
    state["events"].append(event(3, "REVOKE", trust.key_id,
                                 WHEN - timedelta(hours=2),
                                 approval_ref="APPROVAL-REVOKE"))
    state["revision"] = len(state["events"])
    set_history(gov, history, checkpoint, state)
    history.record = old
    fails("CHECKPOINT_MISMATCH", args)


def test_old_checkpoint_or_missing_checkpoint_blocks_new_history():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    before = checkpoint.checkpoint
    state["events"].append(event(3, "RENEW", trust.key_id,
                                 WHEN - timedelta(days=2),
                                 valid_to=WHEN + timedelta(days=50),
                                 approval_ref="APPROVAL-RENEW"))
    state["revision"] = len(state["events"])
    set_history(gov, history, checkpoint, state)
    checkpoint.checkpoint = before
    fails("CHECKPOINT_MISMATCH", args)
    checkpoint.checkpoint = None
    fails("CHECKPOINT_UNAVAILABLE", args)


def test_signature_invalid_even_if_checkpoint_matches_rewritten_payload():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    other = Ed25519PrivateKey.generate()
    set_history(other, history, checkpoint, state)
    fails("LIFECYCLE_SIGNATURE_INVALID", args)


def test_attacker_self_reported_root_is_not_allowed_as_replacement():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    rogue = Ed25519PrivateKey.generate()
    set_history(rogue, history, checkpoint, state)
    # The only root is pinned in host config, not read from the payload.
    fails("LIFECYCLE_SIGNATURE_INVALID", args)


def test_cross_company_governance_is_not_accepted():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    with pytest.raises(ParameterVersionBindingError) as ex:
        GovernedParameterVersionSource(
            company_id=COMPANY_A, issuer_id=trust.issuer_id, key_id=trust.key_id,
            governance_key=replace(root, company_id=COMPANY_B),
            history_repository=history, checkpoint_source=checkpoint,
            record_repository=records, verification_at=WHEN,
        )
    assert ex.value.code == "GOVERNANCE_COMPANY_MISMATCH"
    with pytest.raises(ParameterVersionBindingError) as ex:
        args["version_source"].get_version_manifest(
            COMPANY_B, payload["parameters_version"], WHEN,
        )
    assert ex.value.code == "COMPANY_SCOPE_MISMATCH"


def test_missing_providers_fail_closed_without_creating_keys_or_storage():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    base = dict(
        company_id=COMPANY_A, issuer_id=trust.issuer_id, key_id=trust.key_id,
        governance_key=root, history_repository=history,
        checkpoint_source=checkpoint, record_repository=records,
        verification_at=WHEN,
    )
    for field, code in (
        ("governance_key", "GOVERNANCE_TRUST_MISSING"),
        ("history_repository", "HISTORY_SOURCE_MISSING"),
        ("checkpoint_source", "CHECKPOINT_SOURCE_MISSING"),
        ("record_repository", "VERSION_SOURCE_UNAVAILABLE"),
    ):
        with pytest.raises(ParameterVersionBindingError) as ex:
            GovernedParameterVersionSource(**dict(base, **{field: None}))
        assert ex.value.code == code
    source = args["version_source"]
    for prohibited in ("register_key", "authorize_key", "revoke_key", "save_version", "apply_change"):
        assert not hasattr(source, prohibited)


def test_expired_or_future_dated_lifecycle_blocks_even_signed_version():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    state["expires_at"] = (WHEN - timedelta(seconds=1)).isoformat()
    set_history(gov, history, checkpoint, state)
    fails("LIFECYCLE_STALE", args)
    state["expires_at"] = (WHEN + timedelta(days=1)).isoformat()
    state["issued_at"] = (WHEN + timedelta(seconds=1)).isoformat()
    set_history(gov, history, checkpoint, state)
    fails("LIFECYCLE_STALE", args)


def test_fake_extra_or_duplicate_json_member_not_authoritative():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    extra = dict(state, public_key_hex="attacker")
    set_history(gov, history, checkpoint, extra)
    fails("INVALID_LIFECYCLE_HISTORY", args)
    raw = _canonical(state)[:-1] + b',"company_id":"OTHER"}'
    history.record = SignedKeyLifecycleHistory(raw, gov.sign(raw))
    checkpoint.checkpoint = IndependentLifecycleCheckpoint(
        COMPANY_A, trust.issuer_id, state["revision"],
        sha256(raw).hexdigest(),
    )
    fails("INVALID_SIGNED_RECORD", args)


def test_invalid_sequence_or_action_or_missing_approval_ref_fails():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    invalid = json.loads(json.dumps(state))
    invalid["events"][1]["sequence"] = 3
    set_history(gov, history, checkpoint, invalid)
    fails("INVALID_LIFECYCLE_EVENT", args)
    invalid = json.loads(json.dumps(state))
    invalid["events"][1]["approval_ref"] = None
    set_history(gov, history, checkpoint, invalid)
    fails("INVALID_SIGNED_RECORD", args)
    invalid = json.loads(json.dumps(state))
    invalid["events"][1]["action"] = "AUTO_APPROVE"
    set_history(gov, history, checkpoint, invalid)
    fails("INVALID_LIFECYCLE_EVENT", args)


def test_cannot_replay_different_issuer_or_key_under_same_company():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    state["issuer_id"] = "OTHER-ISSUER"
    set_history(gov, history, checkpoint, state)
    fails("CHECKPOINT_SCOPE_MISMATCH", args)
    state["issuer_id"] = trust.issuer_id
    set_history(gov, history, checkpoint, state)
    args["version_source"] = GovernedParameterVersionSource(
        company_id=COMPANY_A, issuer_id=trust.issuer_id, key_id="OTHER-KEY",
        governance_key=root, history_repository=history,
        checkpoint_source=checkpoint, record_repository=records,
        verification_at=WHEN,
    )
    fails("KEY_NOT_ENROLLED", args)


def test_manifest_drift_and_missing_c0_evidence_still_fail_closed():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    args["evidence_by_parameter"] = {}
    fails("INCOMPLETE_DOCUMENTARY_COVERAGE", args)
    args["evidence_by_parameter"] = signed_fixture()[0]["evidence_by_parameter"]
    center.configs[0] = replace(center.configs[0], value="No")
    fails("VERSION_CONTENT_MISMATCH", args)


def test_checkpoint_changes_during_one_manifest_read_are_rejected():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    prior = history.record
    prior_checkpoint = checkpoint.checkpoint
    state["events"].append(event(
        3, "RENEW", trust.key_id, WHEN - timedelta(days=2),
        valid_to=WHEN + timedelta(days=50), approval_ref="APPROVAL-RENEW",
    ))
    state["revision"] = 3
    latest = bind_history(gov, state)
    latest_checkpoint = checkpoint_for(latest, state)

    class SwitchingHistory:
        calls = 0
        def get_signed_history(self, *inputs):
            self.calls += 1
            return prior if self.calls == 1 else latest

    class SwitchingCheckpoint:
        calls = 0
        def get_checkpoint(self, *inputs):
            self.calls += 1
            return prior_checkpoint if self.calls == 1 else latest_checkpoint

    args["version_source"] = GovernedParameterVersionSource(
        company_id=COMPANY_A, issuer_id=trust.issuer_id, key_id=trust.key_id,
        governance_key=root, history_repository=SwitchingHistory(),
        checkpoint_source=SwitchingCheckpoint(), record_repository=records,
        verification_at=WHEN,
    )
    fails("KEY_LIFECYCLE_CHANGED", args)


def test_authorized_rotation_to_new_key_requires_own_enrolment_and_approval():
    a = sample()
    args, records, center, private, payload, trust, gov, root, history, checkpoint, state = a
    new_private = Ed25519PrivateKey.generate()
    new_pub = raw_public(new_private)
    new_id = "SYNTHETIC-KEY-2"
    new_enroll = enroll(new_id, new_pub, at=WHEN - timedelta(days=3))
    new_enroll["sequence"] = 3
    state["events"].append(new_enroll)
    state["events"].append(event(
        4, "AUTHORIZE", new_id, WHEN - timedelta(days=2),
        approval_ref="APPROVAL-NEW-KEY",
    ))
    state["events"].append(event(
        5, "REVOKE", trust.key_id, WHEN - timedelta(days=1),
        approval_ref="APPROVAL-OLD-KEY-RETIRE",
    ))
    state["revision"] = len(state["events"])
    set_history(gov, history, checkpoint, state)
    fails("KEY_REVOKED", args)

    # Re-sign the EXISTING F2.4 selection manifest, but with newly approved key.
    next_manifest = dict(payload, key_id=new_id)
    raw = _canonical(next_manifest)
    records.records[0] = SignedParameterVersionRecord(raw, new_private.sign(raw))
    args["version_source"] = GovernedParameterVersionSource(
        company_id=COMPANY_A, issuer_id=trust.issuer_id, key_id=new_id,
        governance_key=root, history_repository=history,
        checkpoint_source=checkpoint, record_repository=records,
        verification_at=WHEN,
    )
    assert read_version_bound_parameter_selection(**args).lookup.complete_documentary_coverage


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__]))
