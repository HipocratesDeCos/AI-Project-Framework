from decimal import Decimal

from eios.core.execution_boundary import BoundaryStatus, ExecutionPlan, execute_plan
from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.orchestration import O1ExecutionStatus
from eios.rules import build_rules_engine_c0_invoker


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-RULES-E2E",
        scenario_id="S-RULES-E2E",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-RULES-E2E",
        scenario_id="S-RULES-E2E",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-11",
    )


def _assessment(
    rule_id: str,
    *,
    status: str = "EVALUABLE",
    outcome: str | None = "TRUE",
) -> Assessment:
    return Assessment(
        rule_id=rule_id,
        status=status,
        outcome=outcome,
        evidence_ids=[f"EV-{rule_id}"],
        reason=f"{rule_id} assessment.",
    )


def _execute(invoker):
    return execute_plan(
        _purchase(),
        _context(),
        ExecutionPlan(capabilities=("C0",), policy_version="E2E-RULES-v1"),
        {"C0": invoker},
    )


def test_rules_engine_invoker_completes_as_c0_capability() -> None:
    outcome = _execute(
        build_rules_engine_c0_invoker(
            assessments=(
                _assessment("R-FIN-001", outcome="FALSE"),
                _assessment("R-STK-003", outcome="TRUE"),
            ),
            base_result="COMPRAR",
        )
    )

    assert outcome.status == BoundaryStatus.COMPLETED
    assert len(outcome.capability_results) == 1
    capability = outcome.capability_results[0]
    assert capability.capability == "C0"
    assert capability.status == O1ExecutionStatus.COMPLETED
    assert capability.result_available is True
    assert len(capability.trace_references) == 2


def test_rules_engine_invoker_propagates_not_evaluable_to_boundary() -> None:
    outcome = _execute(
        build_rules_engine_c0_invoker(
            assessments=(
                _assessment("R-FIN-001", status="NOT_EVALUABLE", outcome=None),
            ),
            base_result="COMPRAR",
        )
    )

    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    capability = outcome.capability_results[0]
    assert capability.capability == "C0"
    assert capability.status == O1ExecutionStatus.NOT_EVALUABLE
    assert capability.result_available is False
    assert outcome.unresolved_items == ("C0_NOT_EVALUABLE",)


def test_rules_engine_invoker_empty_set_remains_explicitly_not_evaluable() -> None:
    outcome = _execute(
        build_rules_engine_c0_invoker(
            assessments=(),
            base_result="COMPRAR",
        )
    )

    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("C0_NO_ASSESSMENTS",)


def test_rules_engine_invoker_unknown_rule_fails_closed_in_boundary() -> None:
    outcome = _execute(
        build_rules_engine_c0_invoker(
            assessments=(_assessment("R-PRE-001"),),
            base_result="COMPRAR",
        )
    )

    assert outcome.status == BoundaryStatus.FAILED
    assert outcome.failure_reason is not None
    assert outcome.failure_reason.startswith("C0:")
    assert "no materializada" in outcome.failure_reason


def test_rules_engine_invoker_freezes_assessment_snapshot() -> None:
    source = _assessment("R-STK-003", outcome="FALSE")
    invoker = build_rules_engine_c0_invoker(
        assessments=(source,),
        base_result="COMPRAR",
    )

    source.status = "NOT_EVALUABLE"
    source.outcome = None
    source.reason = "mutated after invoker construction"

    outcome = _execute(invoker)

    assert outcome.status == BoundaryStatus.COMPLETED
    capability = outcome.capability_results[0]
    assert capability.status == O1ExecutionStatus.COMPLETED
    assert capability.result_available is True
