from datetime import date
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.data_sufficiency import (
    DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
    DecisionEvidenceRequirementSet,
    DecisionEvidenceSufficiencyProducer,
    RequirementEvidenceBinding,
    decision_evidence_purchase_ref,
    decision_evidence_sufficiency_ref,
)
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.data_quality import R_DAT_003, evaluate_r_dat_003


EVAL_DATE = date(2026, 9, 21)


def _context():
    return DecisionContext(
        decision_id="DEC-DAT003",
        scenario_id="SCN-DAT003",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="DEC-DAT003",
        scenario_id="SCN-DAT003",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("100"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _requirement_set(requirement_ids=("REQ-A", "REQ-B")):
    return DecisionEvidenceRequirementSet(
        decision_id=_context().decision_id,
        scenario_id=_context().scenario_id,
        data_snapshot_id=_context().data_snapshot_id,
        company_scope="COMPANY-A",
        purchase_operation_ref=decision_evidence_purchase_ref(_purchase()),
        effective_date=EVAL_DATE,
        requirement_set_id="REQSET-DAT003",
        requirement_set_version="v1",
        requirement_ids=requirement_ids,
        authority_ref="DAT003-AUTH-v0.1",
        methodology_ref="DAT003-METHOD-v0.1",
        trace_refs=("TRACE-REQSET",),
    )


def _demonstrated(evidence_id, demonstration_ref):
    return Evidence(
        evidence_id=evidence_id,
        source_type="RequirementEvidence",
        source_ref=f"source:{evidence_id}",
        captured_at=EVAL_DATE,
        state="DEMONSTRATED",
        demonstration_ref=demonstration_ref,
    )


def _gap(evidence_id):
    return Evidence(
        evidence_id=evidence_id,
        source_type="RequirementEvidence",
        source_ref=f"source:{evidence_id}",
        captured_at=EVAL_DATE,
        state="GAP",
    )


def _binding(requirement_id, classification):
    if classification == "SATISFIED":
        return RequirementEvidenceBinding(
            requirement_id=requirement_id,
            classification=classification,
            evidence=(_demonstrated(f"EV-{requirement_id}", f"ok:{requirement_id}"),),
            classification_ref=f"classification:{requirement_id}:satisfied",
            authority_ref="REQ-AUTH-v1",
        )
    if classification == "FAILED":
        return RequirementEvidenceBinding(
            requirement_id=requirement_id,
            classification=classification,
            evidence=(_demonstrated(f"EV-{requirement_id}", f"failed:{requirement_id}"),),
            classification_ref=f"classification:{requirement_id}:failed",
            authority_ref="REQ-AUTH-v1",
        )
    return RequirementEvidenceBinding(
        requirement_id=requirement_id,
        classification="UNDETERMINED",
        evidence=(_gap(f"EV-{requirement_id}"),),
        authority_ref="REQ-AUTH-v1",
    )


def _producer():
    return DecisionEvidenceSufficiencyProducer(
        authority_ref="DAT003-AUTH-v0.1",
        methodology_ref="DAT003-METHOD-v0.1",
    )


def _observation(classifications=("SATISFIED", "SATISFIED")):
    req = _requirement_set()
    bindings = tuple(
        _binding(requirement_id, classification)
        for requirement_id, classification in zip(req.requirement_ids, classifications)
    )
    return _producer().produce(
        purchase=_purchase(),
        context=_context(),
        company_scope="COMPANY-A",
        state="AVAILABLE",
        requirement_set=req,
        bindings=bindings,
        source_ref="sufficiency-source",
        trace_refs=("TRACE-SUFF",),
    )


def _sufficiency_evidence(obs, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-DAT003",
        source_type=DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
        source_ref="sufficiency-source",
        captured_at=EVAL_DATE,
        state=state,
        demonstration_ref=(
            decision_evidence_sufficiency_ref(obs)
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _evaluate(obs):
    return evaluate_r_dat_003(
        _purchase(),
        _context(),
        authorized_rule(R_DAT_003, "rules-v1"),
        obs,
        _sufficiency_evidence(obs),
    )


def test_all_required_satisfied_is_false():
    result = _evaluate(_observation(("SATISFIED", "SATISFIED")))
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


@pytest.mark.parametrize(
    "classifications",
    (
        ("FAILED", "SATISFIED"),
        ("UNDETERMINED", "SATISFIED"),
        ("FAILED", "UNDETERMINED"),
    ),
)
def test_failed_or_undetermined_is_true(classifications):
    result = _evaluate(_observation(classifications))
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_gap_is_undetermined_not_failed():
    obs = _observation(("UNDETERMINED", "SATISFIED"))
    assert obs.undetermined_requirement_ids == ("REQ-A",)
    assert obs.failed_requirement_ids == ()


def test_failed_requires_demonstrated_evidence():
    with pytest.raises(ValueError, match="Evidence válida/demostrada"):
        RequirementEvidenceBinding(
            requirement_id="REQ-A",
            classification="FAILED",
            evidence=(_gap("EV-GAP"),),
            classification_ref="classification:failed",
            authority_ref="REQ-AUTH-v1",
        )


def test_missing_requirement_binding_is_structural_error():
    req = _requirement_set()
    with pytest.raises(ValueError, match="cubrir exactamente"):
        _producer().produce(
            purchase=_purchase(),
            context=_context(),
            company_scope="COMPANY-A",
            state="AVAILABLE",
            requirement_set=req,
            bindings=(_binding("REQ-A", "SATISFIED"),),
            source_ref="sufficiency-source",
        )


def test_empty_requirement_set_fails_closed_as_not_determinable():
    req = _requirement_set(())
    obs = _producer().produce(
        purchase=_purchase(),
        context=_context(),
        company_scope="COMPANY-A",
        state="AVAILABLE",
        requirement_set=req,
        bindings=(),
        source_ref="sufficiency-source",
    )
    assert obs.state == "NOT_DETERMINABLE"
    result = _evaluate(obs)
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


@pytest.mark.parametrize(
    "state",
    ("NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"),
)
def test_non_available_observation_is_not_evaluable(state):
    obs = _producer().produce(
        purchase=_purchase(),
        context=_context(),
        company_scope="COMPANY-A",
        state=state,
        requirement_set=None,
        bindings=(),
        source_ref="sufficiency-source",
    )
    result = _evaluate(obs)
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_sufficiency_evidence_gap_is_not_evaluable():
    obs = _observation()
    result = evaluate_r_dat_003(
        _purchase(),
        _context(),
        authorized_rule(R_DAT_003, "rules-v1"),
        obs,
        _sufficiency_evidence(obs, state="GAP"),
    )
    assert result.status == "NOT_EVALUABLE"


def test_forged_sufficiency_evidence_is_structural_error():
    obs = _observation()
    with pytest.raises(ValueError, match="no está vinculada"):
        evaluate_r_dat_003(
            _purchase(),
            _context(),
            authorized_rule(R_DAT_003, "rules-v1"),
            obs,
            _sufficiency_evidence(obs, demonstration_ref="forged"),
        )


def test_requirement_set_is_exactly_bound_to_purchase():
    req = _requirement_set().model_copy(update={"purchase_operation_ref": "forged"})
    with pytest.raises(ValueError, match="PurchaseOperation exacta"):
        _producer().produce(
            purchase=_purchase(),
            context=_context(),
            company_scope="COMPANY-A",
            state="AVAILABLE",
            requirement_set=req,
            bindings=(
                _binding("REQ-A", "SATISFIED"),
                _binding("REQ-B", "SATISFIED"),
            ),
            source_ref="sufficiency-source",
        )


def test_metadata_is_r0_critical_with_insufficient_result():
    metadata = authorized_rule_metadata(R_DAT_003, "rules-v1")
    assert metadata.effect == "R0"
    assert metadata.severity == "CRÍTICA"
    assert metadata.active_result == "INFORMACIÓN INSUFICIENTE"


def test_no_dat_parameters_or_quality_gate_consumed():
    import inspect
    import eios.rules.data_quality as module

    source = inspect.getsource(module.evaluate_r_dat_003)
    assert "P-DAT-003" not in source
    assert "P-DAT-007" not in source
    assert "QualityTrustResult" not in source
