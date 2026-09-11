from datetime import date
from decimal import Decimal

import pytest

from eios.core.crc_mvp import RuleMetadata
from eios.core.models import Assessment, DecisionContext, PurchaseOperation, Rule
from eios.core.orchestration import O1ExecutionStatus
from eios.rules import run_assessment_vertical


CONTEXT = DecisionContext(
    decision_id="D-RUNTIME",
    scenario_id="S-RUNTIME",
    rules_version="rules-v1",
    parameters_version="params-v1",
    data_snapshot_id="snapshot-v1",
)
PURCHASE = PurchaseOperation(
    decision_id="D-RUNTIME",
    scenario_id="S-RUNTIME",
    article_id="A-1",
    supplier_id="SUP-1",
    quantity=Decimal("10"),
    unit_price=Decimal("5"),
    currency="EUR",
    operation_date=date(2026, 9, 11),
)
RULE = Rule(rule_id="R-X-001", version="rules-v1", requires_evidence=True)
METADATA = RuleMetadata(
    rule_id="R-X-001",
    version="rules-v1",
    effect="R2",
    severity="ALTA",
)


def _assessment(status="EVALUABLE", outcome="TRUE") -> Assessment:
    return Assessment(
        rule_id="R-X-001",
        status=status,
        outcome=outcome if status == "EVALUABLE" else None,
        evidence_ids=["EV-1"],
        reason="runtime test",
    )


def test_true_assessment_flows_through_trace_crc_and_o1() -> None:
    result = run_assessment_vertical(
        purchase=PURCHASE,
        context=CONTEXT,
        rule=RULE,
        assessment=_assessment(),
        base_result="COMPRAR",
        rule_metadata=METADATA,
    )

    assert result.trace.rule_id == "R-X-001"
    assert result.c0_capability.status == O1ExecutionStatus.COMPLETED
    assert result.crc_result.consolidated_result == "NEGOCIAR"
    assert result.support_package.execution_status == O1ExecutionStatus.COMPLETED
    assert result.support_package.trace_references == (result.trace.trace_id,)


def test_false_assessment_preserves_base_result() -> None:
    result = run_assessment_vertical(
        purchase=PURCHASE,
        context=CONTEXT,
        rule=RULE,
        assessment=_assessment(outcome="FALSE"),
        base_result="COMPRAR CONDICIONADO",
        rule_metadata=METADATA,
    )
    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"


def test_not_evaluable_propagates_without_becoming_false() -> None:
    result = run_assessment_vertical(
        purchase=PURCHASE,
        context=CONTEXT,
        rule=RULE,
        assessment=_assessment(status="NOT_EVALUABLE"),
        base_result="COMPRAR",
        rule_metadata=METADATA,
    )
    assert result.crc_result.consolidated_result == "INFORMACIÓN INSUFICIENTE"
    assert result.c0_capability.status == O1ExecutionStatus.NOT_EVALUABLE
    assert result.support_package.execution_status == O1ExecutionStatus.PARTIALLY_COMPLETED


def test_runtime_rejects_assessment_from_another_rule() -> None:
    foreign = _assessment().model_copy(update={"rule_id": "R-OTHER"})
    with pytest.raises(ValueError, match="Assessment.rule_id"):
        run_assessment_vertical(
            purchase=PURCHASE,
            context=CONTEXT,
            rule=RULE,
            assessment=foreign,
            base_result="COMPRAR",
            rule_metadata=METADATA,
        )


def test_runtime_rejects_metadata_from_another_rule_or_version() -> None:
    wrong = RuleMetadata(
        rule_id="R-X-001",
        version="rules-other",
        effect="R2",
        severity="ALTA",
    )
    with pytest.raises(ValueError, match="RuleMetadata.version"):
        run_assessment_vertical(
            purchase=PURCHASE,
            context=CONTEXT,
            rule=RULE,
            assessment=_assessment(),
            base_result="COMPRAR",
            rule_metadata=wrong,
        )


def test_trace_id_is_reproducible_for_same_material() -> None:
    first = run_assessment_vertical(
        purchase=PURCHASE,
        context=CONTEXT,
        rule=RULE,
        assessment=_assessment(),
        base_result="COMPRAR",
        rule_metadata=METADATA,
    )
    second = run_assessment_vertical(
        purchase=PURCHASE,
        context=CONTEXT,
        rule=RULE,
        assessment=_assessment(),
        base_result="COMPRAR",
        rule_metadata=METADATA,
    )
    assert first.trace.trace_id == second.trace.trace_id
    assert first.trace.input_fingerprint == second.trace.input_fingerprint
