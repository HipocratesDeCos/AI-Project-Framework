"""F2.4: version correspondence, tenant isolation and fail-closed manifests.

The in-memory source is a synthetic fixture, NOT an authenticated version
authority or a production repository.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from eios.parameters import (
    ParameterVersionBindingError,
    ParameterVersionManifest,
    VersionBoundParameterSelection,
    fingerprint_parameter_selection,
    read_version_bound_parameter_selection,
)
from eios.payment_term_control import resolve_payment_term_control

from test_company_parameter_resolution_api import (
    AFTER, BEFORE, COMPANY_A, COMPANY_B, OTHER, PID, WHEN,
    configuration, context, make_center, proof, query,
)


class SyntheticVersionSource:
    def __init__(self, *manifests):
        self.manifests = {
            (m.company_id, m.parameters_version, m.effective_at): m
            for m in manifests
        }
        self.calls = []

    def get_version_manifest(self, company_id, parameters_version, effective_at):
        self.calls.append((company_id, parameters_version, effective_at))
        return self.manifests.get((company_id, parameters_version, effective_at))


def samples(*, company=COMPANY_A, value="Sí", version="VERSION-1",
            configs=None, ids=(PID,), at=WHEN):
    configs = configs or (configuration(company, value, cid=10 if company == COMPANY_A else 20),)
    center, repo = make_center(*configs)
    evidence = {
        cfg.parameter_id: proof(cfg, when=at, evidence_id="DOC-" + cfg.parameter_id)
        for cfg in configs
        if cfg.parameter_id in ids
    }
    lookup = query(
        center, company, at=at, ids=ids, evidence=evidence,
        ctx=context(version),
    )
    digest = fingerprint_parameter_selection(lookup)
    manifest = ParameterVersionManifest(
        company_id=company, parameters_version=version,
        effective_at=at, parameter_ids=ids,
        selection_fingerprint=digest,
        source_ref="SYNTHETIC-AUTHORITY-SOURCE-" + company,
    )
    source = SyntheticVersionSource(manifest)
    args = dict(
        center=center, version_source=source,
        company_id=company, expected_company_id=company,
        context=context(version), effective_at=at,
        parameter_ids=ids, evidence_by_parameter=evidence,
    )
    return args, source, repo, manifest


def run(args):
    return read_version_bound_parameter_selection(**args)


def raises_code(args, expected):
    with pytest.raises(ParameterVersionBindingError) as exc:
        run(args)
    assert exc.value.code == expected


def test_complete_selection_matched_to_existing_context_version_without_authority():
    args, source, repo, manifest = samples()
    record = run(args)
    assert isinstance(record, VersionBoundParameterSelection)
    assert record.lookup.parameters_version == "VERSION-1"
    assert record.manifest is manifest
    assert record.selection_fingerprint == manifest.selection_fingerprint
    assert record.version_attestation == "MATCHED_SUPPLIED_VERSION_SOURCE"
    assert record.source_authentication == "ADAPTER_RESPONSIBILITY"
    assert record.atomicity == "MANIFEST_CONSISTENCY_NOT_DB_TRANSACTION"
    assert record.decision_authority is False
    assert record.operational_path == "FORBIDDEN"
    assert record.lookup.complete_documentary_coverage
    assert source.calls == [(COMPANY_A, "VERSION-1", WHEN)] * 2


def test_same_scenario_two_synthetic_companies_select_distinct_versions_of_policy():
    first = configuration(COMPANY_A, "Sí", cid=31)
    second = configuration(COMPANY_B, "No", cid=31)
    center, repo = make_center(first, second)
    outcomes = {}
    digests = set()
    for company, conf in ((COMPANY_A, first), (COMPANY_B, second)):
        evidence = {PID: proof(conf, evidence_id="E-" + company)}
        lookup = query(center, company, evidence=evidence)
        manifest = ParameterVersionManifest(
            company, "VERSION-1", WHEN, (PID,),
            fingerprint_parameter_selection(lookup),
            "TRUSTED-TEST-SOURCE-" + company,
        )
        bound = read_version_bound_parameter_selection(
            center=center, version_source=SyntheticVersionSource(manifest),
            company_id=company, expected_company_id=company,
            context=context(), effective_at=WHEN, parameter_ids=(PID,),
            evidence_by_parameter=evidence,
        )
        entry = bound.lookup.entries[0]
        control = resolve_payment_term_control(
            context=context(), company_scope=company,
            evaluation_date=WHEN.date(),
            control_resolution=entry.resolution,
            control_evidence=entry.evidence,
        )
        outcomes[company] = control.state
        digests.add(bound.selection_fingerprint)
    assert outcomes == {COMPANY_A: "ENABLED", COMPANY_B: "DISABLED"}
    assert len(digests) == 2


def test_selection_fingerprint_is_order_independent_but_set_complete():
    a = configuration(cid=10)
    b = configuration(pid=OTHER, value="2000", cid=11)
    args, source, _, manifest = samples(configs=(a, b), ids=(PID, OTHER))
    result = run(args)
    assert len(result.lookup.entries) == 2
    assert result.selection_fingerprint == manifest.selection_fingerprint
    args["parameter_ids"] = (OTHER, PID)
    # The manifest represents an exact set, independent of UI input ordering.
    assert run(args).selection_fingerprint == manifest.selection_fingerprint


def test_manifest_missing_one_required_parameter_cannot_be_used():
    a = configuration(cid=10)
    b = configuration(pid=OTHER, value="2000", cid=11)
    args, source, repo, manifest = samples(configs=(a, b), ids=(PID, OTHER))
    source.manifests[(COMPANY_A, "VERSION-1", WHEN)] = replace(
        manifest, parameter_ids=(PID,),
    )
    raises_code(args, "MANIFEST_SELECTION_MISMATCH")
    assert repo.calls == [(COMPANY_A, PID, WHEN), (COMPANY_A, OTHER, WHEN)]


def test_change_of_parameter_value_after_manifest_creation_is_detected():
    args, source, repo, _ = samples()
    repo.configs[0] = replace(repo.configs[0], value="No")
    raises_code(args, "VERSION_CONTENT_MISMATCH")


def test_change_of_configuration_id_after_manifest_is_detected():
    args, source, repo, _ = samples()
    repo.configs[0] = replace(repo.configs[0], configuration_id=99)
    raises_code(args, "VERSION_CONTENT_MISMATCH")


def test_change_of_validity_interval_after_manifest_is_detected():
    args, source, repo, _ = samples()
    repo.configs[0] = replace(repo.configs[0], valid_to=AFTER + timedelta(days=1))
    raises_code(args, "VERSION_CONTENT_MISMATCH")


def test_later_policy_revision_without_new_manifest_is_not_same_version():
    args, source, repo, _ = samples()
    repo.configs[0] = replace(repo.configs[0], value="No", updated_at=WHEN)
    args["context"] = context("VERSION-2")
    # A different declared version has no authorized manifest.
    raises_code(args, "VERSION_SOURCE_UNAVAILABLE")


def test_same_manifest_version_cannot_be_reused_for_another_company():
    args, source, _, manifest = samples()
    args["company_id"] = COMPANY_B
    args["expected_company_id"] = COMPANY_B
    source.manifests[(COMPANY_B, "VERSION-1", WHEN)] = manifest
    raises_code(args, "MANIFEST_COMPANY_MISMATCH")


def test_untrusted_company_scope_rejected_before_center_or_version_source():
    args, source, repo, _ = samples()
    args["expected_company_id"] = COMPANY_B
    raises_code(args, "COMPANY_SCOPE_MISMATCH")
    assert source.calls == []


def test_manifest_from_another_parameter_version_fails_before_reading_center():
    args, source, repo, manifest = samples()
    source.manifests[(COMPANY_A, "VERSION-1", WHEN)] = replace(
        manifest, parameters_version="OTHER-VERSION",
    )
    raises_code(args, "MANIFEST_VERSION_MISMATCH")


def test_manifest_different_cutoff_is_rejected():
    args, source, _, manifest = samples()
    source.manifests[(COMPANY_A, "VERSION-1", WHEN)] = replace(
        manifest, effective_at=WHEN + timedelta(days=1),
    )
    raises_code(args, "MANIFEST_CUTOFF_MISMATCH")


def test_version_source_with_no_manifest_fails_closed():
    args, _, _, _ = samples()
    args["version_source"] = SyntheticVersionSource()
    raises_code(args, "VERSION_SOURCE_UNAVAILABLE")


def test_missing_version_port_does_not_fall_back_to_context_string():
    args, _, _, _ = samples()
    args["version_source"] = object()
    raises_code(args, "VERSION_SOURCE_UNAVAILABLE")


def test_untyped_version_manifest_does_not_pass():
    args, source, _, _ = samples()
    key = (COMPANY_A, "VERSION-1", WHEN)
    source.manifests[key] = {"parameters_version": "VERSION-1"}
    raises_code(args, "INVALID_VERSION_MANIFEST")


def test_incomplete_documentary_evidence_cannot_be_version_matched():
    args, _, _, _ = samples()
    args["evidence_by_parameter"] = {}
    raises_code(args, "INCOMPLETE_DOCUMENTARY_COVERAGE")


def test_wrong_documentary_evidence_cannot_be_version_matched():
    args, _, _, _ = samples()
    args["evidence_by_parameter"][PID] = args["evidence_by_parameter"][PID].model_copy(
        update={"source_ref": "other-company-source"},
    )
    raises_code(args, "INCOMPLETE_DOCUMENTARY_COVERAGE")


def test_manifest_reused_between_different_selection_values_is_blocked():
    args, source, repo, manifest = samples()
    second = configuration(pid=PID, value="No")
    repo.configs[0] = second
    raises_code(args, "VERSION_CONTENT_MISMATCH")


def test_version_source_changed_between_two_reads_is_detected():
    args, source, _, manifest = samples()
    original = source.get_version_manifest

    def changed_on_second_read(*request):
        if source.calls:
            return replace(manifest, source_ref="SECOND-SOURCE-REF")
        return original(*request)

    source.get_version_manifest = changed_on_second_read
    raises_code(args, "VERSION_SOURCE_CHANGED")


def test_mutation_of_context_by_source_does_not_relabel_selection():
    args, source, _, manifest = samples()
    original = source.get_version_manifest

    def mutate_context(*request):
        args["context"].parameters_version = "TAMPERED"
        return original(*request)

    source.get_version_manifest = mutate_context
    bound = run(args)
    assert bound.lookup.parameters_version == "VERSION-1"
    assert bound.manifest.parameters_version == "VERSION-1"


def test_mutation_of_evidence_by_source_does_not_rewrite_receipt():
    args, source, _, manifest = samples()
    original = source.get_version_manifest

    def mutate_evidence(*request):
        args["evidence_by_parameter"][PID].source_ref = "tampered-mid-read"
        return original(*request)

    source.get_version_manifest = mutate_evidence
    result = run(args)
    assert result.lookup.complete_documentary_coverage
    assert result.lookup.entries[0].evidence.source_ref != "tampered-mid-read"


@pytest.mark.parametrize("invalid", [
    (), (PID, PID), (PID, ""), (PID, " P-FIN-002"),
])
def test_incomplete_or_duplicate_selection_rejected_before_source(invalid):
    args, source, repo, _ = samples()
    args["parameter_ids"] = invalid
    raises_code(args, "INVALID_SELECTION")
    assert source.calls == []


@pytest.mark.parametrize("bad_digest", ["", "xyz", "F" * 64, "z" * 64])
def test_noncanonical_manifest_fingerprint_rejected(bad_digest):
    args, source, _, manifest = samples()
    source.manifests[(COMPANY_A, "VERSION-1", WHEN)] = replace(
        manifest, selection_fingerprint=bad_digest,
    )
    raises_code(args, "INVALID_VERSION_MANIFEST")


def test_manifest_duplicate_parameter_ids_cannot_claim_completeness():
    args, source, _, manifest = samples()
    source.manifests[(COMPANY_A, "VERSION-1", WHEN)] = replace(
        manifest, parameter_ids=(PID, PID),
    )
    raises_code(args, "INVALID_VERSION_MANIFEST")


def test_manifest_missing_provenance_reference_rejected():
    args, source, _, manifest = samples()
    source.manifests[(COMPANY_A, "VERSION-1", WHEN)] = replace(
        manifest, source_ref="",
    )
    raises_code(args, "INVALID_IDENTITY")


def test_naive_timestamp_cannot_bind_version():
    args, source, _, _ = samples()
    args["effective_at"] = datetime(2026, 10, 1, 9)
    raises_code(args, "INVALID_EFFECTIVE_AT")


def test_version_binding_receipt_is_frozen_and_no_rule_authority():
    args, source, _, _ = samples()
    receipt = run(args)
    with pytest.raises(FrozenInstanceError):
        receipt.decision_authority = True
    assert not hasattr(receipt, "assessment")
    assert not hasattr(receipt, "approval")


def test_selection_hash_changes_when_context_version_changes_even_same_values():
    args, _, _, _ = samples()
    original = query(
        args["center"], COMPANY_A, evidence=args["evidence_by_parameter"],
        ctx=context("VERSION-1"),
    )
    different = query(
        args["center"], COMPANY_A, evidence=args["evidence_by_parameter"],
        ctx=context("VERSION-2"),
    )
    assert fingerprint_parameter_selection(original) != fingerprint_parameter_selection(different)
