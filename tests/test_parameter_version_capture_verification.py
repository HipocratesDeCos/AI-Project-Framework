"""F2.4: a full documented selection must equal one immutable DIP capture."""
from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest

from eios.core.decision_input_package import build_decision_input_package
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.parameters import (
    ParameterCaptureVerificationError,
    configuration_evidence_source_ref,
    read_company_parameters_for_context,
    verify_company_parameter_capture,
)
from eios.parameters.center import (
    Configuration, ParameterConfigurationCenter, ParameterDefinition,
)
from eios.parameters.resolution import resolve_configuration_for_context


WHEN = datetime(2026, 10, 1, 9, tzinfo=timezone.utc)
PID = "P-PAG-004"
OTHER = "P-FIN-002"
A, B = "COMPANY-A", "COMPANY-B"


def context(version="PARAMETERS-1", snapshot="SNAP-1", rules="RULES-1"):
    return DecisionContext(
        decision_id="DECISION-1", scenario_id="SCENARIO-1",
        rules_version=rules, parameters_version=version,
        data_snapshot_id=snapshot,
    )


def config(pid=PID, company=A, value=None, cid=10):
    return Configuration(
        configuration_id=cid, parameter_id=pid, company_id=company,
        value=value if value is not None else ("Sí" if pid == PID else "500"),
        value_type="BOOLEAN" if pid == PID else "DECIMAL",
        unit=None if pid == PID else "EUR",
        valid_from=WHEN - timedelta(days=10), valid_to=WHEN + timedelta(days=10),
        created_at=WHEN - timedelta(days=10),
        updated_at=WHEN - timedelta(days=10),
    )


class Repository:
    def __init__(self, *configs):
        self.rows = {(c.company_id, c.parameter_id): c for c in configs}
        self.calls = []

    def get_at(self, company, pid, at):
        self.calls.append((company, pid, at))
        c = self.rows.get((company, pid))
        return c if c and c.valid_from <= at < c.valid_to else None


def make_center(*configs):
    repository = Repository(*configs)
    catalogue = SimpleNamespace(get_parameter=lambda pid: (
        ParameterDefinition(
            pid, value_type="BOOLEAN" if pid == PID else "DECIMAL",
            unit=None if pid == PID else "EUR",
        ) if pid in (PID, OTHER) else None
    ))
    return ParameterConfigurationCenter(
        catalogue, SimpleNamespace(can_modify=lambda *args: False), repository,
    ), repository


def proof(c, at=WHEN, eid=None):
    resolution = resolve_configuration_for_context(c, context(), at)
    return Evidence(
        evidence_id=eid or "E-" + c.parameter_id,
        source_type="ParameterConfigurationEvidence",
        source_ref=configuration_evidence_source_ref(
            company_id=c.company_id, parameter_id=c.parameter_id,
            configuration_id=c.configuration_id,
        ),
        captured_at=at.date(), state="DEMONSTRATED",
        demonstration_ref=resolution.configuration_ref,
    )


def make_lookup(center, company, ctx, ids, proofs, at=WHEN):
    return read_company_parameters_for_context(
        center=center, company_id=company, expected_company_id=company,
        context=ctx, effective_at=at, parameter_ids=ids,
        evidence_by_parameter=proofs,
    )


def make_package(center, company, ctx, ids, proofs, at=WHEN):
    return build_decision_input_package(
        purchase=PurchaseOperation(
            decision_id=ctx.decision_id, scenario_id=ctx.scenario_id,
            article_id="SKU-1", supplier_id="SUP-1", quantity=Decimal("2"),
            unit_price=Decimal("12.5"), operation_date=date(2026, 10, 1),
        ),
        context=ctx, evidence=tuple(proofs.values()),
        financial_snapshot=None, company_id=company, effective_at=at,
        requested_parameter_ids=ids, center=center,
    )


def setup_two(company=A, version="PARAMETERS-1"):
    first = config(company=company, cid=10)
    second = config(OTHER, company=company, cid=11)
    center, repository = make_center(first, second)
    ctx = context(version)
    ids = (PID, OTHER)
    evidences = {PID: proof(first), OTHER: proof(second)}
    dip = make_package(center, company, ctx, ids, evidences)
    lookup = make_lookup(center, company, ctx, ids, evidences)
    return center, repository, ctx, ids, evidences, dip, lookup


def test_full_two_parameter_capture_matches_and_retains_non_authentication():
    _, repo, ctx, ids, evidence, dip, lookup = setup_two()
    matched = verify_company_parameter_capture(lookup=lookup, package=dip, context=ctx)
    assert matched.capture_status == "MATCHED_DIP_CAPTURE_ONLY"
    assert matched.company_id == A
    assert matched.parameter_ids == ids
    assert matched.parameters_version == "PARAMETERS-1"
    assert matched.dip_fingerprint == dip.fingerprint
    assert matched.version_attestation == "HISTORICAL_VERSION_NOT_ATTESTED"
    assert matched.origin_attestation == "NOT_EXTERNALLY_AUTHENTICATED"
    assert matched.decision_authority is False
    assert matched.operational_path == "FORBIDDEN"
    assert len(repo.calls) == 4  # DIP + lookup; no writes or second registry
    with pytest.raises(FrozenInstanceError):
        matched.parameters_version = "COUNTERFEIT"


def test_cross_company_dip_rejected_even_when_version_and_configuration_ids_match():
    _, _, ctx, ids, _, dip_a, _ = setup_two(A)
    _, _, _, _, _, _, lookup_b = setup_two(B)
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(lookup=lookup_b, package=dip_a, context=ctx)
    assert err.value.code == "DIP_COMPANY_MISMATCH"


def test_same_configuration_id_but_changed_value_cannot_pass_capture():
    center, repo, ctx, ids, proofs, dip, _ = setup_two()
    repo.rows[(A, PID)] = replace(repo.rows[(A, PID)], value="No")
    updated_lookup = make_lookup(center, A, ctx, ids, proofs)
    assert updated_lookup.complete_documentary_coverage
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(
            lookup=updated_lookup, package=dip, context=ctx,
        )
    assert err.value.code == "DIP_CONFIGURATION_MISMATCH"


def test_dip_must_include_all_requested_parameter_configurations():
    first = config()
    center, _ = make_center(first)
    ctx = context()
    ids = (PID, OTHER)
    proofs = {PID: proof(first)}
    dip = make_package(center, A, ctx, ids, proofs)
    lookup = make_lookup(center, A, ctx, ids, proofs)
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(lookup=lookup, package=dip, context=ctx)
    assert err.value.code == "DIP_INCOMPLETE"


def test_lookup_without_full_documentary_coverage_is_not_a_match():
    center, _, ctx, ids, proofs, dip, _ = setup_two()
    partial = make_lookup(center, A, ctx, ids, {PID: proofs[PID]})
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(lookup=partial, package=dip, context=ctx)
    assert err.value.code == "LOOKUP_INCOMPLETE"


def test_same_version_label_does_not_hide_different_selection():
    center, _, ctx, ids, proofs, _, lookup = setup_two()
    partial_dip = make_package(center, A, ctx, (PID,), {PID: proofs[PID]})
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(lookup=lookup, package=partial_dip, context=ctx)
    assert err.value.code == "DIP_SELECTION_MISMATCH"


def test_dip_selection_order_must_be_identical_not_silently_zipped():
    center, _, ctx, ids, proofs, _, lookup = setup_two()
    reordered = make_package(center, A, ctx, tuple(reversed(ids)), proofs)
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(lookup=lookup, package=reordered, context=ctx)
    assert err.value.code == "DIP_SELECTION_MISMATCH"


@pytest.mark.parametrize("changed", [
    context(version="OTHER-VERSION"),
    context(snapshot="OTHER-SNAPSHOT"),
    context(rules="OTHER-RULES"),
])
def test_dip_context_mismatch_detects_version_snapshot_and_rules(changed):
    center, _, ctx, ids, proofs, _, lookup = setup_two()
    mismatched = make_package(center, A, changed, ids, proofs)
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(lookup=lookup, package=mismatched, context=ctx)
    assert err.value.code == "DIP_CONTEXT_MISMATCH"


def test_expected_context_must_agree_with_lookup_before_dip():
    _, _, _, _, _, dip, lookup = setup_two()
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(
            lookup=lookup, package=dip, context=context(version="OTHER"),
        )
    assert err.value.code == "LOOKUP_CONTEXT_MISMATCH"


def test_cutoff_mismatch_fails_even_when_configurations_remain_valid():
    center, _, ctx, ids, proofs, _, lookup = setup_two()
    later = WHEN + timedelta(days=1)
    later_proofs = {
        pid: proof(center.get_configuration_at(A, pid, later), at=later)
        for pid in ids
    }
    later_dip = make_package(center, A, ctx, ids, later_proofs, at=later)
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(lookup=lookup, package=later_dip, context=ctx)
    assert err.value.code == "DIP_EFFECTIVE_AT_MISMATCH"


def test_same_configuration_different_evidence_cannot_be_swapped_between_captures():
    center, _, ctx, ids, proofs, dip, _ = setup_two()
    alternate = dict(proofs)
    alternate[PID] = proof(config(), eid="E-DIFFERENT")
    lookup = make_lookup(center, A, ctx, ids, alternate)
    assert lookup.complete_documentary_coverage
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(lookup=lookup, package=dip, context=ctx)
    assert err.value.code == "DIP_EVIDENCE_MISMATCH"


def test_missing_parameter_proof_from_dip_is_not_accepted():
    center, _, ctx, ids, proofs, _, lookup = setup_two()
    dip = make_package(center, A, ctx, ids, {PID: proofs[PID]})
    with pytest.raises(ParameterCaptureVerificationError) as err:
        verify_company_parameter_capture(lookup=lookup, package=dip, context=ctx)
    assert err.value.code == "DIP_EVIDENCE_SELECTION_MISMATCH"


def test_independent_copies_and_stable_capture_digest_after_caller_mutations():
    _, _, ctx, _, proofs, dip, lookup = setup_two()
    result = verify_company_parameter_capture(lookup=lookup, package=dip, context=ctx)
    original = dip.fingerprint
    ctx.parameters_version = "MUTATED"
    proofs[PID].source_ref = "fabricated"
    dip.evidence[0].source_ref = "not-persisted"
    assert dip.fingerprint == original
    assert result.dip_fingerprint == original
    assert result.parameters_version == "PARAMETERS-1"
