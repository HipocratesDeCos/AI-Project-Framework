from decimal import Decimal
from inspect import signature

import pytest

import eios.mvp as mvp
from eios.core.c0_reproducibility import build_trace
from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus
from eios.rules import (
    AssessmentTraceBinding,
    RulesEngineInput,
    authorized_rule,
    implemented_rule_ids,
    run_rules_engine,
)
from eios.rules.orchestrator import DecisionRuleExecutionResult, StockExcessRuleInputs


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-MVP-SVC",
        scenario_id="S-MVP-SVC",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-MVP-SVC",
        scenario_id="S-MVP-SVC",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-11",
    )


def _quality_invoker(purchase: PurchaseOperation, context: DecisionContext):
    assert purchase.decision_id == "D-MVP-SVC"
    assert purchase.scenario_id == "S-MVP-SVC"
    assert context.decision_id == "D-MVP-SVC"
    assert context.scenario_id == "S-MVP-SVC"
    return CapabilityExecution(
        capability="QTG",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=("trace-qtg",),
    )


def _tco_invoker(purchase: PurchaseOperation, context: DecisionContext):
    assert purchase.decision_id == "D-MVP-SVC"
    assert purchase.scenario_id == "S-MVP-SVC"
    assert context.decision_id == "D-MVP-SVC"
    assert context.scenario_id == "S-MVP-SVC"
    return CapabilityExecution(
        capability="TCO",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
    )


def _decision_twin_invoker(purchase: PurchaseOperation, context: DecisionContext):
    assert purchase.decision_id == "D-MVP-SVC"
    assert context.decision_id == "D-MVP-SVC"
    return CapabilityExecution(
        capability="DECISION_TWIN",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=("trace-twin",),
    )


def _rules_result() -> DecisionRuleExecutionResult:
    purchase = _purchase()
    context = _context()
    assessment = Assessment(
        rule_id="R-STK-003",
        status="EVALUABLE",
        outcome="TRUE",
        evidence_ids=["EV-STK"],
        reason="Exceso demostrado.",
    )
    rule = authorized_rule(assessment.rule_id, context.rules_version)
    trace = build_trace(
        context,
        purchase,
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    engine_result = run_rules_engine(
        RulesEngineInput(
            purchase=purchase,
            context=context,
            bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
            base_result="COMPRAR",
        )
    )
    return DecisionRuleExecutionResult(
        executed_rule_ids=("R-STK-003",),
        omitted_rule_ids=tuple(
            rule_id for rule_id in implemented_rule_ids() if rule_id != "R-STK-003"
        ),
        rules_engine_result=engine_result,
    )


def test_vertical_service_runs_non_rule_capabilities_directly():
    result = mvp.run_vertical_mvp_support(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-1",
        base_result="COMPRAR",
        quality_invoker=_quality_invoker,
        tco_invoker=_tco_invoker,
        decision_twin_invoker=_decision_twin_invoker,
    )

    assert result.status == BoundaryStatus.COMPLETED
    assert result.rules is None
    assert result.crc_result is None
    assert tuple(item.capability for item in result.capability_results) == (
        "QTG",
        "TCO",
        "DECISION_TWIN",
    )


def test_vertical_service_exposes_rules_crc_and_e2e_in_same_result(monkeypatch):
    fake_rules = _rules_result()

    def fake_run_domain_rules(**kwargs):
        assert kwargs["base_result"] == "COMPRAR"
        assert kwargs["stock_excess"] is not None
        return fake_rules

    monkeypatch.setattr(mvp, "run_domain_rules", fake_run_domain_rules)
    marker = object()
    result = mvp.run_vertical_mvp_support(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-1",
        base_result="COMPRAR",
        stock_excess=StockExcessRuleInputs(marker, marker),
        quality_invoker=_quality_invoker,
        tco_invoker=_tco_invoker,
    )

    assert result.status == BoundaryStatus.COMPLETED
    assert tuple(item.capability for item in result.capability_results) == (
        "QTG",
        "TCO",
        "C0",
    )
    assert result.executed_rule_ids == ("R-STK-003",)
    assert "R-FIN-001" in result.omitted_rule_ids
    assert result.crc_result is not None
    assert result.crc_result.consolidated_result == "NEGOCIAR"


def test_vertical_service_signature_has_no_detached_opaque_results():
    parameters = signature(mvp.run_vertical_mvp_support).parameters

    assert "quality_result" not in parameters
    assert "price_result" not in parameters
    assert "tco_result" not in parameters
    assert "decision_twin_result" not in parameters
    assert "quality_invoker" in parameters
    assert "price_invoker" in parameters
    assert "tco_invoker" in parameters
    assert "decision_twin_invoker" in parameters


def test_vertical_service_requires_at_least_one_supplied_capability():
    with pytest.raises(ValueError, match="al menos una capacidad"):
        mvp.run_vertical_mvp_support(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-E2E-1",
            base_result="COMPRAR",
        )
