from decimal import Decimal

import pytest

from eios.core.c0_reproducibility import build_trace
from eios.core.execution_boundary import BoundaryStatus, ExecutionPlan, execute_plan
from eios.core.models import Assessment, DecisionContext, PurchaseOperation, Rule
from eios.core.orchestration import O1ExecutionStatus
from eios.rules import (
    AssessmentTraceBinding,
    authorized_rule,
    build_rules_engine_c0_invoker,
)


def _context(
    *,
    decision_id: str = "D-RULES-E2E",
    scenario_id: str = "S-RULES-E2E",
) -> DecisionContext:
    return DecisionContext(
        decision_id=decision_id,
        scenario_id=scenario_id,
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase(
    *,
    decision_id: str = "D-RULES-E2E",
    scenario_id: str = "S-RULES-E2E",
) -> PurchaseOperation:
    return PurchaseOperation(
        decision_id=decision_id,
        scenario_id=scenario_id,
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


def _binding(
    rule_id: str,
    *,
    status: str = "EVALUABLE",
    outcome: str | None = "TRUE",
) -> AssessmentTraceBinding:
    assessment = _assessment(rule_id, status=status, outcome=outcome)
    rule = authorized_rule(rule_id, _context().rules_version)
    trace = build_trace(
        _context(),
        _purchase(),
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    return AssessmentTraceBinding(assessment=assessment, trace=trace)


def _execute(invoker, *, purchase=None, context=None):
    operation = purchase or _purchase()
    execution_context = context or _context()
    return execute_plan(
        operation,
        execution_context,
        ExecutionPlan(capabilities=("C0",), policy_version="E2E-RULES-v1"),
        {"C0": invoker},
    )


def test_rules_engine_invoker_completes_as_c0_capability() -> None:
    outcome = _execute(
        build_rules_engine_c0_invoker(
            bindings=(
                _binding("R-FIN-001", outcome="FALSE"),
                _binding("R-STK-003", outcome="TRUE"),
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
            bindings=(
                _binding("R-FIN-001", status="NOT_EVALUABLE", outcome=None),
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
            bindings=(),
            base_result="COMPRAR",
        )
    )

    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("C0_NO_ASSESSMENTS",)


def test_rules_engine_invoker_unknown_rule_fails_closed_in_boundary() -> None:
    assessment = _assessment("R-PRE-001")
    rule = Rule(rule_id="R-PRE-001", version="rules-v1", requires_evidence=True)
    trace = build_trace(
        _context(),
        _purchase(),
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    binding = AssessmentTraceBinding(assessment=assessment, trace=trace)

    outcome = _execute(
        build_rules_engine_c0_invoker(
            bindings=(binding,),
            base_result="COMPRAR",
        )
    )

    assert outcome.status == BoundaryStatus.FAILED
    assert outcome.failure_reason is not None
    assert outcome.failure_reason.startswith("C0:")
    assert "no materializada" in outcome.failure_reason


def test_rules_engine_invoker_freezes_binding_snapshot() -> None:
    source = _binding("R-STK-003", outcome="FALSE")
    invoker = build_rules_engine_c0_invoker(
        bindings=(source,),
        base_result="COMPRAR",
    )

    source.assessment.status = "NOT_EVALUABLE"
    source.assessment.outcome = None
    source.assessment.reason = "mutated after invoker construction"

    outcome = _execute(invoker)

    assert outcome.status == BoundaryStatus.COMPLETED
    capability = outcome.capability_results[0]
    assert capability.status == O1ExecutionStatus.COMPLETED
    assert capability.result_available is True


def test_rules_engine_invoker_cannot_reuse_binding_in_foreign_context() -> None:
    invoker = build_rules_engine_c0_invoker(
        bindings=(_binding("R-STK-003"),),
        base_result="COMPRAR",
    )
    foreign_context = _context(decision_id="D-OTHER", scenario_id="S-OTHER")
    foreign_purchase = _purchase(decision_id="D-OTHER", scenario_id="S-OTHER")

    outcome = _execute(
        invoker,
        purchase=foreign_purchase,
        context=foreign_context,
    )

    assert outcome.status == BoundaryStatus.FAILED
    assert outcome.failure_reason is not None
    assert "Trace.decision_id" in outcome.failure_reason


def test_generic_invoker_rejects_legacy_assessments_keyword() -> None:
    with pytest.raises(TypeError, match="assessments"):
        build_rules_engine_c0_invoker(
            assessments=(_assessment("R-STK-003"),),
            base_result="COMPRAR",
        )
