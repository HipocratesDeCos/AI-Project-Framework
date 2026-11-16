"""F3.3: real Ed25519 verification of external version records.

All private signing keys are generated in-memory by these synthetic tests.
None is committed to the repository or considered a real company credential.
"""
from dataclasses import replace
from datetime import timedelta
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from eios.parameters.signed_version_source import (
    SCHEMA,
    Ed25519VerifiedParameterVersionSource,
    SignedParameterVersionRecord,
    TrustedIssuerPublicKey,
)
from eios.parameters.version_binding import (
    ParameterVersionBindingError, read_version_bound_parameter_selection,
)
from test_parameter_version_selection_binding import (
    COMPANY_A, COMPANY_B, WHEN, samples,
)


class Records:
    def __init__(self, *records):
        self.records = list(records)
        self.calls = []

    def get_signed_record(self, company_id, parameters_version, effective_at):
        self.calls.append((company_id, parameters_version, effective_at))
        return self.records[0] if self.records else None


def _canonical(payload):
    return json.dumps(
        payload, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _signed(private, payload):
    raw = _canonical(payload)
    return SignedParameterVersionRecord(raw, private.sign(raw))


def fixture(*, company=COMPANY_A, value="Sí"):
    args, _, repo, manifest = samples(company=company, value=value)
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    trust = TrustedIssuerPublicKey(
        company_id=company, issuer_id="TEST-CORPORATE-ISSUER",
        key_id="SYNTHETIC-KEY-1", public_key_bytes=public,
        valid_from=WHEN - timedelta(days=30),
        valid_to=WHEN + timedelta(days=30),
    )
    payload = {
        "schema": SCHEMA, "company_id": company,
        "issuer_id": trust.issuer_id, "key_id": trust.key_id,
        "parameters_version": manifest.parameters_version,
        "effective_at": WHEN.isoformat(),
        "parameter_ids": list(manifest.parameter_ids),
        "selection_fingerprint": manifest.selection_fingerprint,
        "source_ref": "synthetic-signed-version:" + company,
        "issued_at": (WHEN - timedelta(days=1)).isoformat(),
        "expires_at": (WHEN + timedelta(days=7)).isoformat(),
    }
    records = Records(_signed(private, payload))
    source = Ed25519VerifiedParameterVersionSource(
        record_repository=records, trusted_key=trust,
        expected_company_id=company, verification_at=WHEN,
    )
    args["version_source"] = source
    return args, records, repo, private, payload, trust


def fails(code, args):
    with pytest.raises(ParameterVersionBindingError) as error:
        read_version_bound_parameter_selection(**args)
    assert error.value.code == code


def test_real_signed_payload_matches_full_f24_selection_and_withholds_authority():
    args, records, repo, private, payload, trust = fixture()
    receipt = read_version_bound_parameter_selection(**args)
    assert receipt.manifest.company_id == COMPANY_A
    assert receipt.manifest.parameters_version == payload["parameters_version"]
    assert receipt.manifest.selection_fingerprint == receipt.selection_fingerprint
    assert receipt.manifest.source_ref == payload["source_ref"]
    assert receipt.version_attestation == "MATCHED_SUPPLIED_VERSION_SOURCE"
    assert receipt.source_authentication == "ADAPTER_RESPONSIBILITY"
    assert receipt.decision_authority is False
    assert receipt.operational_path == "FORBIDDEN"
    assert receipt.lookup.complete_documentary_coverage
    assert len(records.calls) == 2


def test_no_source_record_fails_closed_without_querying_center():
    args, records, repo, *_ = fixture()
    records.records.clear()
    fails("VERSION_SOURCE_UNAVAILABLE", args)
    assert repo.calls == [(COMPANY_A, "P-PAG-004", WHEN)]


def test_tampered_signed_payload_is_refused_before_center_access():
    args, records, repo, private, payload, trust = fixture()
    damaged = dict(payload, source_ref="attacker:replacement")
    records.records = [SignedParameterVersionRecord(_canonical(damaged), records.records[0].signature)]
    before = len(repo.calls)
    fails("SIGNATURE_INVALID", args)
    assert len(repo.calls) == before


def test_wrong_trust_anchor_public_key_rejects_valid_signature():
    args, records, repo, private, payload, trust = fixture()
    stranger = Ed25519PrivateKey.generate().public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    args["version_source"] = Ed25519VerifiedParameterVersionSource(
        record_repository=records,
        trusted_key=replace(trust, public_key_bytes=stranger),
        expected_company_id=COMPANY_A, verification_at=WHEN,
    )
    fails("SIGNATURE_INVALID", args)


def test_cross_company_key_or_request_is_denied():
    args, records, repo, private, payload, trust = fixture()
    with pytest.raises(ParameterVersionBindingError) as err:
        Ed25519VerifiedParameterVersionSource(
            record_repository=records,
            trusted_key=replace(trust, company_id=COMPANY_B),
            expected_company_id=COMPANY_A,
            verification_at=WHEN,
        )
    assert err.value.code == "TRUST_SCOPE_MISMATCH"
    with pytest.raises(ParameterVersionBindingError) as err:
        args["version_source"].get_version_manifest(
            COMPANY_B, payload["parameters_version"], WHEN,
        )
    assert err.value.code == "COMPANY_SCOPE_MISMATCH"


@pytest.mark.parametrize("field,new_value,code", [
    ("issuer_id", "FALSE-ISSUER", "SIGNED_SCOPE_MISMATCH"),
    ("key_id", "OTHER-KEY", "SIGNED_SCOPE_MISMATCH"),
    ("company_id", COMPANY_B, "SIGNED_SCOPE_MISMATCH"),
    ("parameters_version", "OTHER-VERSION", "SIGNED_SCOPE_MISMATCH"),
    ("effective_at", (WHEN + timedelta(days=1)).isoformat(), "SIGNED_CUTOFF_MISMATCH"),
    ("schema", "OTHER-SCHEMA", "INVALID_SIGNED_RECORD"),
])
def test_even_re_signed_wrong_identity_cannot_override_host_scope(field, new_value, code):
    args, records, repo, private, payload, trust = fixture()
    records.records[0] = _signed(private, dict(payload, **{field: new_value}))
    fails(code, args)


@pytest.mark.parametrize("edit,code", [
    (lambda p: {**p, "issued_at": (WHEN + timedelta(days=1)).isoformat()}, "SIGNED_RECORD_EXPIRED"),
    (lambda p: {**p, "expires_at": (WHEN - timedelta(days=1)).isoformat()}, "SIGNED_RECORD_EXPIRED"),
    (lambda p: {**p, "issued_at": (WHEN - timedelta(days=60)).isoformat()}, "SIGNING_KEY_NOT_VALID"),
])
def test_re_signed_expired_future_or_out_of_key_window_record_is_rejected(edit, code):
    args, records, repo, private, payload, trust = fixture()
    records.records[0] = _signed(private, edit(payload))
    fails(code, args)


def test_missing_key_trust_or_provider_cannot_activate_version():
    _, records, repo, private, payload, trust = fixture()
    with pytest.raises(ParameterVersionBindingError) as err:
        Ed25519VerifiedParameterVersionSource(
            record_repository=records, trusted_key=None,
            expected_company_id=COMPANY_A, verification_at=WHEN,
        )
    assert err.value.code == "TRUST_ANCHOR_MISSING"
    with pytest.raises(ParameterVersionBindingError) as err:
        Ed25519VerifiedParameterVersionSource(
            record_repository=None, trusted_key=trust,
            expected_company_id=COMPANY_A, verification_at=WHEN,
        )
    assert err.value.code == "REPOSITORY_UNAVAILABLE"


def test_unknown_selection_version_cannot_inherit_signature_of_other_version():
    args, records, repo, private, payload, trust = fixture()
    args["context"] = args["context"].model_copy(
        update={"parameters_version": "OTHER-VERSION"},
    )
    fails("SIGNED_SCOPE_MISMATCH", args)


def test_signed_fingerprint_cannot_be_used_to_forge_live_configurations():
    args, records, repo, private, payload, trust = fixture()
    repo.configs[0] = replace(repo.configs[0], value="No")
    fails("VERSION_CONTENT_MISMATCH", args)


def test_two_companies_with_distinct_trust_anchors_do_not_share_version_source():
    first = fixture(company=COMPANY_A, value="Sí")
    second = fixture(company=COMPANY_B, value="No")
    output_a = read_version_bound_parameter_selection(**first[0])
    output_b = read_version_bound_parameter_selection(**second[0])
    assert output_a.manifest.company_id == COMPANY_A
    assert output_b.manifest.company_id == COMPANY_B
    assert output_a.selection_fingerprint != output_b.selection_fingerprint


def test_missing_documentary_evidence_cannot_be_replaced_with_signed_manifest():
    args, records, repo, private, payload, trust = fixture()
    args["evidence_by_parameter"] = {}
    fails("INCOMPLETE_DOCUMENTARY_COVERAGE", args)


def test_tampered_manifest_even_with_valid_signature_disagrees_with_center():
    args, records, repo, private, payload, trust = fixture()
    records.records[0] = _signed(
        private, dict(payload, selection_fingerprint="0" * 64),
    )
    fails("VERSION_CONTENT_MISMATCH", args)


def test_changed_manifest_between_two_reads_fails_closed():
    args, records, repo, private, payload, trust = fixture()
    original = records.records[0]

    class Drifting:
        count = 0
        def get_signed_record(self, *arguments):
            self.count += 1
            if self.count == 1:
                return original
            return _signed(private, dict(payload, source_ref="changed-source"))

    args["version_source"] = Ed25519VerifiedParameterVersionSource(
        record_repository=Drifting(), trusted_key=trust,
        expected_company_id=COMPANY_A, verification_at=WHEN,
    )
    fails("VERSION_SOURCE_CHANGED", args)


def test_duplicate_json_members_even_with_valid_signature_are_rejected():
    args, records, repo, private, payload, trust = fixture()
    raw = records.records[0].payload
    tampered = raw[:-1] + b',"company_id":"OTHER"}'
    records.records[0] = SignedParameterVersionRecord(tampered, private.sign(tampered))
    fails("INVALID_SIGNED_RECORD", args)


def test_noncanonical_json_even_with_valid_signature_is_rejected():
    args, records, repo, private, payload, trust = fixture()
    pretty = json.dumps(payload, sort_keys=True, indent=2).encode()
    records.records[0] = SignedParameterVersionRecord(pretty, private.sign(pretty))
    fails("INVALID_SIGNED_RECORD", args)


def test_missing_or_extra_signed_fields_are_rejected():
    args, records, repo, private, payload, trust = fixture()
    del payload["source_ref"]
    records.records[0] = _signed(private, payload)
    fails("INVALID_SIGNED_RECORD", args)
    args, records, repo, private, payload, trust = fixture()
    payload["public_key_bytes"] = "self-reported-attacker-key"
    records.records[0] = _signed(private, payload)
    fails("INVALID_SIGNED_RECORD", args)


def test_parameter_selection_must_be_canonical_and_complete():
    args, records, repo, private, payload, trust = fixture()
    records.records[0] = _signed(private, dict(
        payload, parameter_ids=["P-PAG-004", "P-PAG-004"],
    ))
    fails("INVALID_SIGNED_RECORD", args)
    args, records, repo, private, payload, trust = fixture()
    records.records[0] = _signed(private, dict(
        payload, parameter_ids=["P-PAG-004", "P-STK-002"],
    ))
    fails("MANIFEST_SELECTION_MISMATCH", args)


def test_boolean_success_does_not_create_operational_authority_or_persistence():
    args, records, repo, private, payload, trust = fixture()
    source = args["version_source"]
    assert source.decision_authority is False
    assert source.operational_path == "FORBIDDEN"
    assert source.source_authentication == (
        "SIGNATURE_VERIFIED_AGAINST_SUPPLIED_TRUST_ANCHOR"
    )
    assert not hasattr(source, "apply_change")
    assert not hasattr(source, "save_version")
    assert read_version_bound_parameter_selection(**args).decision_authority is False
