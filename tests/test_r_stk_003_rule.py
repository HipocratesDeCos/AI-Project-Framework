from datetime import date
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation, Rule
from eios.rules import STOCK_EXCESS_EVIDENCE_SOURCE_TYPE, evaluate_r_stk_003
from eios.stock.models import DataIssueRef, ExcessResult, StockReferenceValue, StockResultIdentity


EVAL = date(2026, 9, 11)
CONTEXT = DecisionContext(
    decision_id="D-STK-RULE",
    scenario_id="S-PURCHASE",
    rules_version="rules-v1",
    parameters_version="params-v1",
    data_snapshot_id="snapshot-v1",
)
PURCHASE = PurchaseOperation(
    decision_id="D-STK-RULE",
    scenario_id="S-PURCHASE",
    article_id="ART-1",
    supplier_id="SUP-1",
    quantity=Decimal("10"),
    unit_price=Decimal("5"),
    currency="EUR",
    operation_date=EVAL,
)
RULE = Rule(rule_id="R-STK-003", version="rules-v1", requires_evidence=True)


def _identity() -> StockResultIdentity:
    return StockResultIdentity(
        decision_id=CONTEXT.decision_id,
        scenario_id=CONTEXT.scenario_id,
        rules_version=CONTEXT.rules_version,
        parameters_version=CONTEXT.parameters_version,
        data_snapshot_id=CONTEXT.data_snapshot_id,
        company_id="COMP-1",
        operational_scope_id="OPS-1",
        article_id=PURCHASE.article_id,
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="0.17",
    )


def _excess(state: str) -> ExcessResult:
    identity = _identity()
    if state == "EXCESS":
        reference_value = Decimal("120")
        values = dict(
            stock_maximum=Decimal("100"),
            excess_tolerance_quantity=Decimal("10"),
            excess_threshold=Decimal("110"),
            excess_quantity=Decimal("10"),
        )
        ref_state = "KNOWN"
    elif state == "WITHIN_TOLERANCE":
        reference_value = Decimal("105")
        values = dict(
            stock_maximum=Decimal("100"),
            excess_tolerance_quantity=Decimal("10"),
            excess_threshold=Decimal("110"),
            excess_quantity=Decimal("0"),
        )
        ref_state = "KNOWN"
    elif state == "NO_EXCESS":
        reference_value = Decimal("90")
        values = dict(
            stock_maximum=Decimal("100"),
            excess_tolerance_quantity=Decimal("10"),
            excess_threshold=Decimal("110"),
            excess_quantity=Decimal("0"),
        )
        ref_state = "KNOWN"
    else:
        reference_value = None
        values = {}
        ref_state = state

    issue_refs = ()
    if state == "NOT_EVIDENCED":
        issue_refs = (
            DataIssueRef(
                issue_id="ISS-STK-MISSING",
                issue_type="MISSING_DATA",
                issue_record_ref="issue:stk:missing",
            ),
        )
    elif state == "CONFLICTING_DATA":
        issue_refs = (
            DataIssueRef(
                issue_id="ISS-STK-CONFLICT",
                issue_type="CONTRADICTION",
                issue_record_ref="issue:stk:conflict",
                evidence_refs=("ev:a", "ev:b"),
            ),
        )

    reference = StockReferenceValue(
        identity=identity,
        reference_kind="PROJECTED",
        reference_date=EVAL,
        value=reference_value,
        unit="unit",
        state=ref_state,
        source_ref="stock-reference:projected",
        issue_refs=issue_refs,
        trace_refs=("trace:stock-reference",),
    )
    return ExcessResult(
        identity=identity,
        stock_reference=reference,
        state=state,
        issue_refs=issue_refs,
        trace_refs=("trace:excess",),
        **values,
    )


def _evidence(state="DEMONSTRATED") -> Evidence:
    return Evidence(
        evidence_id="EV-STK-EXCESS",
        source_type=STOCK_EXCESS_EVIDENCE_SOURCE_TYPE,
        source_ref="eios:stock:m07",
        captured_at=EVAL,
        state=state,
        demonstration_ref="trace:excess" if state == "DEMONSTRATED" else None,
    )


def test_excess_maps_to_true_assessment() -> None:
    assessment = evaluate_r_stk_003(PURCHASE, CONTEXT, RULE, _excess("EXCESS"), _evidence())
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "TRUE"
    assert assessment.evidence_ids == ["EV-STK-EXCESS"]


def test_no_excess_and_within_tolerance_map_to_false() -> None:
    no_excess = evaluate_r_stk_003(PURCHASE, CONTEXT, RULE, _excess("NO_EXCESS"), _evidence())
    tolerance = evaluate_r_stk_003(PURCHASE, CONTEXT, RULE, _excess("WITHIN_TOLERANCE"), _evidence())
    assert no_excess.outcome == "FALSE"
    assert tolerance.outcome == "FALSE"


def test_uncertainty_never_becomes_false() -> None:
    for state in ("UNKNOWN", "NOT_EVIDENCED", "CONFLICTING_DATA"):
        assessment = evaluate_r_stk_003(PURCHASE, CONTEXT, RULE, _excess(state), _evidence())
        assert assessment.status == "NOT_EVALUABLE"
        assert assessment.outcome is None


def test_gap_evidence_blocks_conclusive_m07_result() -> None:
    assessment = evaluate_r_stk_003(PURCHASE, CONTEXT, RULE, _excess("EXCESS"), _evidence("GAP"))
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_rule_requires_projected_stock_reference() -> None:
    excess = _excess("EXCESS")
    current_ref = excess.stock_reference.model_copy(update={"reference_kind": "CURRENT_AVAILABLE"})
    invalid = excess.model_copy(update={"stock_reference": current_ref})
    with pytest.raises(ValueError, match="PROJECTED"):
        evaluate_r_stk_003(PURCHASE, CONTEXT, RULE, invalid, _evidence())


def test_evidence_must_bind_to_m07_provenance() -> None:
    bad = _evidence().model_copy(update={"demonstration_ref": "trace:other"})
    with pytest.raises(ValueError, match="provenance M07"):
        evaluate_r_stk_003(PURCHASE, CONTEXT, RULE, _excess("EXCESS"), bad)
