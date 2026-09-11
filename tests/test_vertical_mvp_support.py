from decimal import Decimal

import pytest

import eios.mvp as mvp
from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus
from eios.quality.gate import QualityTrustResult
from eios.rules.orchestrator import StockExcessRuleInputs
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


def test_vertical_service_runs_non_rule_capabilities_directly():
    outcome = mvp.run_vertical_mvp_support(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-1",
        base_result="COMPRAR",
        quality_result=QualityTrustResult("APTO", "ALTA", ()),
        tco_result=_tco(),
    )

    assert outcome.status == BoundaryStatus.COMPLETED
    assert tuple(item.capability for item in outcome.capability_results) == (
        "QTG",
        "TCO",
    )


def test_vertical_service_adds_c0_when_domain_rule_bundle_is_present(monkeypatch):
    def fake_builder(**kwargs):
        assert kwargs["base_result"] == "COMPRAR"
        assert kwargs["stock_excess"] is not None

        def invoke(*_):
            return CapabilityExecution(
                capability="C0",
                status=O1ExecutionStatus.COMPLETED,
                result_available=True,
                trace_references=("trace-c0",),
            )

        return invoke

    monkeypatch.setattr(mvp, "build_domain_rules_c0_invoker", fake_builder)
    marker = object()
    outcome = mvp.run_vertical_mvp_support(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-1",
        base_result="COMPRAR",
        stock_excess=StockExcessRuleInputs(marker, marker),
        quality_result=QualityTrustResult("APTO", "ALTA", ()),
        tco_result=_tco(),
    )

    assert outcome.status == BoundaryStatus.COMPLETED
    assert tuple(item.capability for item in outcome.capability_results) == (
        "QTG",
        "TCO",
        "C0",
    )


def test_vertical_service_requires_at_least_one_supplied_capability():
    with pytest.raises(ValueError, match="al menos una capacidad"):
        mvp.run_vertical_mvp_support(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-E2E-1",
            base_result="COMPRAR",
        )
