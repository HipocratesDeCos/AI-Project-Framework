from datetime import date

from eios.core.c0 import run_c0
from eios.core.models import DecisionContext, Evidence, InputContract, Rule


def test_c0_end_to_end_preserves_traceable_chain():
    input_contract = InputContract(
        decision_id="DEC-INT-001",
        scenario_id="SCN-INT-001",
        article_id="ART-001",
        supplier_id="PROV-001",
        quantity=25,
        unit_price=10,
        currency="EUR",
        operation_date=date(2026, 8, 21),
    )
    context = DecisionContext(
        decision_id="DEC-INT-001",
        scenario_id="SCN-INT-001",
        rules_version="R-INT-1",
        parameters_version="P-INT-1",
        data_snapshot_id="DS-INT-1",
    )
    evidence = Evidence(
        evidence_id="E-INT-001",
        source_type="ERP",
        source_ref="purchase/INT-001",
        captured_at=date(2026, 8, 21),
        state="DEMONSTRATED",
        demonstration_ref="ERP:purchase/INT-001",
    )
    rule = Rule(rule_id="R-INT-001", version="R-INT-1", requires_evidence=True)

    assessments, traces = run_c0(
        input_contract,
        context,
        [evidence],
        [(rule, lambda purchase, valid_evidence: purchase.unit_price <= 10)],
    )

    assert len(assessments) == len(traces) == 1
    assert assessments[0].status == "EVALUABLE"
    assert assessments[0].outcome == "TRUE"
    assert traces[0].decision_id == context.decision_id
    assert traces[0].scenario_id == context.scenario_id
    assert traces[0].rule_id == rule.rule_id
    assert traces[0].assessment_status == assessments[0].status
    assert traces[0].assessment_outcome == assessments[0].outcome
    assert traces[0].evidence_ids == (evidence.evidence_id,)
