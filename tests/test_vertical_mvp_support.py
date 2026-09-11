from decimal import Decimal

import pytest

import eios.mvp as mvp
from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.quality.gate import QualityTrustResult
from eios.rules import RulesEngineInput, implemented_rule_ids, run_rules_engine
from eios.rules.orchestrator import DecisionRuleExecutionResult, StockExcessRuleInputs
from eios.tco.models import TCOResult


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


def _tco() -> TCOResult:
    return TCOResult(
        decision_id="D-MVP-SVC",
        scenario_id="S-MVP-SVC",
        currency="EUR",
        value=Decimal("55"),
        contributing_components=("purchase",),
        unresolved_components=(),
        limitations=(),
    )


def _rules_result() -> DecisionRuleExecutionResult:
    assessment = Assessment(
        rule_id="R-STK-003",
        status="EVALUABLE",
        outcome="TRUE",
        evidence_ids=["EV-STK"],
        reason="Exceso demostrado.",
    )
    engine_result = run_rules_engine(
        RulesEngineInput(
            purchase=_purchase(),
            context=_context(),
            assessments=(assessment,),
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
        quality_result=QualityTrustResult("APTO", "ALTA", ()),
        tco_result=_tco(),
    )

    assert result.status == BoundaryStatus.COMPLETED
    assert result.rules is None
    assert result.crc_result is None
    assert tuple(item.capability for item in result.capability_results) == (
        "QTG",
        "TCO",
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
        quality_result=QualityTrustResult("APTO", "ALTA", ()),
        tco_result=_tco(),
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


def test_vertical_service_requires_at_least_one_supplied_capability():
    with pytest.raises(ValueError, match="al menos una capacidad"):
        mvp.run_vertical_mvp_support(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-E2E-1",
            base_result="COMPRAR",
        )
