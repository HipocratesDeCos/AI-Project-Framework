"""Regression tests for phase 2.3 public read-only parameter lookup."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from eios.core.models import DecisionContext, Evidence
from eios.parameters import (
    ParameterLookupError,
    configuration_evidence_source_ref,
    read_company_parameters_for_context,
)
from eios.parameters.center import (
    Configuration, ParameterConfigurationCenter, ParameterDefinition,
    ParameterConfigurationError,
)
from eios.parameters.resolution import resolve_configuration_for_context
from eios.payment_term_control import resolve_payment_term_control


WHEN = datetime(2026, 10, 1, 9, tzinfo=timezone.utc)
BEFORE = WHEN - timedelta(days=10)
AFTER = WHEN + timedelta(days=20)
COMPANY_A = "COMPANY-A"
COMPANY_B = "COMPANY-B"
PID = "P-PAG-004"
OTHER = "P-FIN-002"


def context(version="VERSION-1"):
    return DecisionContext(
        decision_id="DECISION-1", scenario_id="SCENARIO-1",
        rules_version="R-V1", parameters_version=version,
        data_snapshot_id="SYNTHETIC-1",
    )


def configuration(company=COMPANY_A, value="Sí", pid=PID, cid=10):
    return Configuration(
        configuration_id=cid, parameter_id=pid, company_id=company,
        value=value, value_type="BOOLEAN" if pid == PID else "DECIMAL",
        unit=None if pid == PID else "EUR",
        valid_from=BEFORE, valid_to=AFTER, created_at=BEFORE, updated_at=BEFORE,
    )


class Catalogue:
    def get_parameter(self, parameter_id):
        if parameter_id == PID:
            return ParameterDefinition(
                PID, value_type="BOOLEAN", unit=None,
                validate_value=lambda value: (
                    None if value in {"Sí", "No"} else "INVALID_VALUE"
                ),
            )
        if parameter_id == OTHER:
            return ParameterDefinition(
                OTHER, value_type="DECIMAL", unit="EUR",
                validate_value=lambda value: (
                    None if value.replace(".", "", 1).isdigit()
                    else "INVALID_VALUE"
                ),
            )
        return None


class Authorization:
    def can_modify(self, company_id, parameter_id, actor):
        return False


class Repository:
    def __init__(self, configs=()):
        self.configs = list(configs)
        self.calls = []

    def get_at(self, company_id, parameter_id, effective_at):
        self.calls.append((company_id, parameter_id, effective_at))
        rows = [
            c for c in self.configs if c.company_id == company_id
            and c.parameter_id == parameter_id
            and c.valid_from <= effective_at < (c.valid_to or AFTER)
        ]
        return rows[0] if rows else None


def make_center(*configs):
    repo = Repository(configs)
    return ParameterConfigurationCenter(Catalogue(), Authorization(), repo), repo


def proof(config, when=WHEN, evidence_id="E1"):
    linked = resolve_configuration_for_context(config, context(), when)
    return Evidence(
        evidence_id=evidence_id,
        source_type="ParameterConfigurationEvidence",
        source_ref=configuration_evidence_source_ref(
            company_id=config.company_id, parameter_id=config.parameter_id,
            configuration_id=config.configuration_id,
        ),
        captured_at=when.date(), state="DEMONSTRATED",
        demonstration_ref=linked.configuration_ref,
    )


def query(center, company=COMPANY_A, at=WHEN, ids=(PID,), evidence=None,
          expected=None, ctx=None):
    return read_company_parameters_for_context(
        center=center, company_id=company,
        expected_company_id=company if expected is None else expected,
        context=context() if ctx is None else ctx, effective_at=at,
        parameter_ids=ids,
        evidence_by_parameter={} if evidence is None else evidence,
    )


def test_company_lookup_reuses_canonical_resolution_and_preserves_context():
    config = configuration()
    center, repo = make_center(config)
    result = query(center, evidence={PID: proof(config)})
    assert result.complete_documentary_coverage
    assert result.company_id == COMPANY_A
    assert result.parameters_version == "VERSION-1"
    assert result.data_snapshot_id == "SYNTHETIC-1"
    entry = result.entries[0]
    assert entry.status == "DOCUMENTARY_CHECK_PASSED"
    assert entry.resolution.value == "Sí"
    assert entry.resolution.parameters_version == result.parameters_version
    assert entry.resolution.configuration_ref == entry.evidence.demonstration_ref
    assert result.version_attestation == "CALLER_CONTEXT_ONLY"
    assert result.origin_attestation == "NOT_EXTERNALLY_AUTHENTICATED"
    assert result.decision_authority is False
    assert result.operational_path == "FORBIDDEN"
    assert repo.calls == [(COMPANY_A, PID, WHEN)]


def test_two_synthetic_companies_same_scenario_get_independent_payment_policy():
    first = configuration(COMPANY_A, "Sí", cid=21)
    second = configuration(COMPANY_B, "No", cid=22)
    center, repo = make_center(first, second)
    outcomes = {}
    for company, config in ((COMPANY_A, first), (COMPANY_B, second)):
        result = query(center, company, evidence={PID: proof(config, evidence_id="E-" + company)})
        entry = result.entries[0]
        # The existing authorized rules retain final control and revalidation.
        control = resolve_payment_term_control(
            context=context(), company_scope=company,
            evaluation_date=WHEN.date(),
            control_resolution=entry.resolution,
            control_evidence=entry.evidence,
        )
        outcomes[company] = control.state
        assert entry.resolution.company_id == company
    assert outcomes == {COMPANY_A: "ENABLED", COMPANY_B: "DISABLED"}
    assert len(repo.calls) == 2


def test_cross_company_evidence_replay_fails_even_with_colliding_configuration_ids():
    first = configuration(COMPANY_A, "Sí", cid=9)
    second = configuration(COMPANY_B, "No", cid=9)
    center, _ = make_center(first, second)
    result = query(
        center, COMPANY_B,
        evidence={PID: proof(first)},
    )
    assert result.entries[0].status == "EVIDENCE_INVALID"
    assert result.entries[0].resolution is None
    assert not result.complete_documentary_coverage


def test_untrusted_caller_cannot_switch_company_scope():
    first = configuration()
    center, repo = make_center(first)
    with pytest.raises(ParameterLookupError) as raised:
        query(center, COMPANY_A, expected=COMPANY_B, evidence={PID: proof(first)})
    assert raised.value.code == "COMPANY_SCOPE_MISMATCH"
    assert repo.calls == []


def test_no_saved_configuration_is_not_filled_with_standard_value():
    center, _ = make_center()
    result = query(center)
    assert not result.complete_documentary_coverage
    assert result.entries[0].status == "CONFIGURATION_ABSENT"
    assert result.entries[0].resolution is None
    assert result.entries[0].evidence is None


def test_no_evidence_does_not_publish_a_resolved_value():
    center, _ = make_center(configuration())
    result = query(center)
    assert result.entries[0].status == "EVIDENCE_MISSING"
    assert result.entries[0].resolution is None
    assert not result.complete_documentary_coverage


@pytest.mark.parametrize("change", [
    {"source_ref": "external:wrong-company"},
    {"source_type": "Invoice"},
    {"captured_at": BEFORE.date()},
    {"demonstration_ref": "parameter_configuration:unknown"},
    {"state": "GAP", "demonstration_ref": None},
])
def test_invalid_or_detached_evidence_never_exposes_resolution(change):
    config = configuration()
    center, _ = make_center(config)
    fake = proof(config).model_copy(update=change)
    result = query(center, evidence={PID: fake})
    assert result.entries[0].status == "EVIDENCE_INVALID"
    assert result.entries[0].resolution is None


def test_parameter_evidence_not_shared_between_two_parameters():
    a = configuration(cid=10)
    b = configuration(pid=OTHER, value="2000", cid=11)
    center, _ = make_center(a, b)
    with pytest.raises(ParameterLookupError) as raised:
        query(center, ids=(PID, OTHER), evidence={
            PID: proof(a, evidence_id="E1"),
            OTHER: proof(b, evidence_id="E1"),
        })
    assert raised.value.code == "EVIDENCE_REUSED"


def test_reading_more_than_one_parameter_does_not_make_partial_data_complete():
    a = configuration()
    b = configuration(pid=OTHER, value="3000", cid=11)
    center, _ = make_center(a, b)
    receipt = query(center, ids=(PID, OTHER), evidence={PID: proof(a)})
    assert tuple(item.status for item in receipt.entries) == (
        "DOCUMENTARY_CHECK_PASSED", "EVIDENCE_MISSING"
    )
    assert receipt.entries[1].resolution is None
    assert not receipt.complete_documentary_coverage


def test_version_context_is_carried_not_claimed_to_be_authenticated():
    config = configuration()
    center, _ = make_center(config)
    result = query(center, evidence={PID: proof(config)},
                   ctx=context("VERSION-EXTERNAL"))
    assert result.parameters_version == "VERSION-EXTERNAL"
    assert result.entries[0].resolution.parameters_version == "VERSION-EXTERNAL"
    assert result.version_attestation == "CALLER_CONTEXT_ONLY"


def test_prior_and_later_cutoff_do_not_reuse_effective_configuration():
    config = configuration()
    center, _ = make_center(config)
    before = query(center, at=BEFORE - timedelta(days=1))
    after = query(center, at=AFTER)
    assert before.entries[0].status == "CONFIGURATION_ABSENT"
    assert after.entries[0].status == "CONFIGURATION_ABSENT"


def test_wrong_company_configuration_from_repository_is_rejected():
    target = configuration(COMPANY_B)
    center, repository = make_center(target)
    repository.get_at = lambda *args: target
    with pytest.raises(ParameterLookupError) as raised:
        query(center, COMPANY_A)
    assert raised.value.code == "CONFIGURATION_SCOPE_MISMATCH"


@pytest.mark.parametrize("change,expected", [
    ({"unit": "days"}, "CONFIGURATION_UNIT_MISMATCH"),
    ({"value_type": "DECIMAL"}, "CONFIGURATION_TYPE_MISMATCH"),
    ({"value": "Maybe"}, "CONFIGURATION_VALUE_INVALID"),
])
def test_catalogue_invariants_remain_authoritative_for_canonical_read(change, expected):
    center, repo = make_center(replace(configuration(), **change))
    with pytest.raises(ParameterLookupError) as raised:
        query(center)
    assert raised.value.code == expected


def test_stale_config_even_from_faulty_repository_does_not_pass():
    stale = replace(configuration(), valid_to=BEFORE + timedelta(days=1))
    center, repo = make_center(stale)
    repo.get_at = lambda *args: stale
    with pytest.raises(ParameterConfigurationError) as raised:
        query(center)
    assert raised.value.code == "INVALID_VALIDITY"


@pytest.mark.parametrize("invalid", [(), (PID, PID), [PID], ("",), (" P-PAG-004",)])
def test_reject_bad_selection_without_effects(invalid):
    center, repo = make_center(configuration())
    with pytest.raises(ParameterLookupError):
        query(center, ids=invalid)
    assert repo.calls == []


def test_extra_evidence_for_unrequested_parameter_rejected():
    center, _ = make_center()
    with pytest.raises(ParameterLookupError) as raised:
        query(center, evidence={OTHER: proof(configuration(pid=OTHER))})
    assert raised.value.code == "EXTRANEOUS_EVIDENCE"


def test_copy_of_evidence_prevents_input_mutation_after_lookup():
    config = configuration()
    center, _ = make_center(config)
    source = proof(config)
    result = query(center, evidence={PID: source})
    source.source_ref = "tampered"
    assert result.entries[0].evidence.source_ref != source.source_ref


def test_no_persistence_or_rule_execution_occurs_in_lookup(monkeypatch):
    import eios.parameters.company_resolution_api as module

    config = configuration()
    center, _ = make_center(config)
    observed = []
    original = module.resolve_configuration_for_context

    def counted(*args, **kwargs):
        observed.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(module, "resolve_configuration_for_context", counted)
    result = query(center, evidence={PID: proof(config)})
    assert result.complete_documentary_coverage
    assert observed == [1]
    assert not hasattr(result, "assessment")
    assert not hasattr(result, "decision")


def test_invalid_datetime_and_unknown_parameter_rejected():
    center, _ = make_center()
    with pytest.raises(ParameterLookupError, match="timezone"):
        query(center, at=datetime(2026, 10, 1, 9))
    with pytest.raises(ParameterConfigurationError) as err:
        query(center, ids=("P-UNKNOWN",))
    assert err.value.code == "PARAMETER_NOT_FOUND"
