from datetime import date

import pytest

from eios.core.c0 import run_c0
from eios.core.models import DecisionContext, Evidence, InputContract, Rule


def make_input() -> InputContract:
    return InputContract(decision_id="DEC-0001", scenario_id="SCN-0001", article_id="ART-001", supplier_id="PROV-001", quantity=100, unit_price=12.50, currency="EUR", operation_date=date(2026, 8, 21))


def make_context() -> DecisionContext:
    return DecisionContext(decision_id="DEC-0001", scenario_id="SCN-0001", rules_version="R-1", parameters_version="P-1", data_snapshot_id="DS-1")


def make_rule() -> Rule:
    return Rule(rule_id="R-PRICE-001", version="R-1", requires_evidence=True)


def demonstrated_evidence() -> Evidence:
    return Evidence(evidence_id="E-001", source_type="ERP", source_ref="purchase-history/001", captured_at=date(2026, 8, 21), state="DEMONSTRATED", demonstration_ref="ERP:purchase-history/001")


def gap_evidence() -> Evidence:
    return Evidence(evidence_id="E-GAP-001", source_type="ERP", source_ref="purchase-history/missing", captured_at=date(2026, 8, 21), state="GAP")


def evaluate(evidence, input_contract=None):
    return run_c0(input_contract or make_input(), make_context(), evidence, [(make_rule(), lambda purchase, valid_evidence: purchase.quantity > 0)])


def test_golden_positive_demonstrated_evidence_evaluates_true():
    assessments, traces = evaluate([demonstrated_evidence()])
    assert assessments[0].status == "EVALUABLE"
    assert assessments[0].outcome == "TRUE"
    assert assessments[0].evidence_ids == ["E-001"]
    assert traces[0].assessment_status == "EVALUABLE"
    assert traces[0].assessment_outcome == "TRUE"
    assert traces[0].evidence_ids == ("E-001",)


def test_golden_negative_gap_evidence_is_not_evaluable():
    assessments, traces = evaluate([gap_evidence()])
    assert assessments[0].status == "NOT_EVALUABLE"
    assert assessments[0].outcome is None
    assert assessments[0].evidence_ids == ["E-GAP-001"]
    assert traces[0].assessment_status == "NOT_EVALUABLE"
    assert traces[0].assessment_outcome is None


def test_absent_evidence_is_not_false():
    assessments, _ = evaluate([])
    assert assessments[0].status == "NOT_EVALUABLE"
    assert assessments[0].outcome is None


def test_rule_without_evidence_requirement_can_evaluate_false():
    rule = Rule(rule_id="R-NO-EVIDENCE", version="R-1", requires_evidence=False)
    assessments, _ = run_c0(make_input(), make_context(), [], [(rule, lambda purchase, evidence: False)])
    assert assessments[0].status == "EVALUABLE"
    assert assessments[0].outcome == "FALSE"


def test_context_mismatch_is_rejected():
    context = make_context().model_copy(update={"scenario_id": "SCN-999"})
    with pytest.raises(ValueError, match="scenario_id"):
        run_c0(make_input(), context, [demonstrated_evidence()], [(make_rule(), lambda purchase, evidence: True)])


def test_rule_version_mismatch_is_rejected():
    rule = make_rule().model_copy(update={"version": "R-2"})
    with pytest.raises(ValueError, match="versión"):
        run_c0(make_input(), make_context(), [demonstrated_evidence()], [(rule, lambda purchase, evidence: True)])


def test_trace_contains_complete_reproducibility_context():
    _, traces = evaluate([demonstrated_evidence()])
    trace = traces[0]
    assert trace.rules_version == "R-1"
    assert trace.parameters_version == "P-1"
    assert trace.data_snapshot_id == "DS-1"
    assert len(trace.input_fingerprint) == 64


def test_trace_identity_changes_when_material_input_changes():
    changed = make_input().model_copy(update={"unit_price": 99.99})
    _, trace_a = evaluate([demonstrated_evidence()])
    _, trace_b = evaluate([demonstrated_evidence()], changed)
    assert trace_a[0].input_fingerprint != trace_b[0].input_fingerprint
    assert trace_a[0].trace_id != trace_b[0].trace_id


def test_trace_identity_is_stable_for_same_material_inputs():
    _, trace_a = evaluate([demonstrated_evidence()])
    _, trace_b = evaluate([demonstrated_evidence()])
    assert trace_a[0].trace_id == trace_b[0].trace_id
