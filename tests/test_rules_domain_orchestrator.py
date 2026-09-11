from decimal import Decimal

import pytest

import eios.rules.orchestrator as orchestrator
from eios.core.models import Assessment, DecisionContext, PurchaseOperation


RULES_VERSION = "rules-v1"
ALL_RULES = (
    "R-ENT-001",
    "R-FIN-001",
    "R-FIN-003",
    "R-HIS-002",
    "R-STK-001",
    "R-STK-003",
    "R-STK-004",
)


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-ORCH",
        scenario_id="S-ORCH",
        rules_version=RULES_VERSION,
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-ORCH",
        scenario_id="S-ORCH",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-11",
    )


def _assessment(rule_id: str, outcome: str) -> Assessment:
    return Assessment(
        rule_id=rule_id,
        status="EVALUABLE",
        outcome=outcome,
        evidence_ids=[f"EV-{rule_id}"],
        reason=f"{rule_id}:{outcome}",
    )


def _patch_rule(monkeypatch, name: str, rule_id: str, outcome: str, calls: list[str]):
    def fake(*args, **kwargs):
        assert args[2].rule_id == rule_id
        assert args[2].version == RULES_VERSION
        calls.append(rule_id)
        return _assessment(rule_id, outcome)

    monkeypatch.setattr(orchestrator, name, fake)


def _all_bundles():
    marker = object()
    return dict(
        delivery=orchestrator.DeliveryRuleInputs(marker, marker, marker, marker),
        stock_excess=orchestrator.StockExcessRuleInputs(marker, marker),
        stock_absorption=orchestrator.StockAbsorptionRuleInputs(marker, marker),
        finance_capacity=orchestrator.FinanceCapacityRuleInputs(
            marker, marker, marker, marker, marker
        ),
        finance_safety_margin=orchestrator.FinanceSafetyMarginRuleInputs(
            marker, marker, marker, marker, marker, marker, marker
        ),
        history_sufficiency=orchestrator.HistorySufficiencyRuleInputs(
            marker, marker, marker, "COMPANY-1", marker, marker
        ),
    )


def test_orchestrator_executes_all_implemented_rule_bridges(monkeypatch):
    calls: list[str] = []
    _patch_rule(monkeypatch, "evaluate_r_ent_001", "R-ENT-001", "TRUE", calls)
    _patch_rule(monkeypatch, "evaluate_r_stk_001", "R-STK-001", "TRUE", calls)
    _patch_rule(monkeypatch, "evaluate_r_stk_003", "R-STK-003", "TRUE", calls)
    _patch_rule(monkeypatch, "evaluate_r_stk_004", "R-STK-004", "TRUE", calls)
    _patch_rule(monkeypatch, "evaluate_r_fin_001", "R-FIN-001", "FALSE", calls)
    _patch_rule(monkeypatch, "evaluate_r_fin_003", "R-FIN-003", "FALSE", calls)
    _patch_rule(monkeypatch, "evaluate_r_his_002", "R-HIS-002", "TRUE", calls)

    result = orchestrator.run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        **_all_bundles(),
    )

    assert calls == [
        "R-ENT-001",
        "R-STK-001",
        "R-STK-003",
        "R-STK-004",
        "R-FIN-001",
        "R-FIN-003",
        "R-HIS-002",
    ]
    assert result.executed_rule_ids == ALL_RULES
    assert result.omitted_rule_ids == ()
    assert tuple(item.rule_id for item in result.assessments) == ALL_RULES
    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"
    assert len(result.traces) == 7
    assert result.c0_capability.result_available is True


def test_delivery_bundle_exposes_stockout_condition_as_r1_and_ent_as_r2(monkeypatch):
    calls: list[str] = []
    _patch_rule(monkeypatch, "evaluate_r_ent_001", "R-ENT-001", "TRUE", calls)
    _patch_rule(monkeypatch, "evaluate_r_stk_001", "R-STK-001", "TRUE", calls)
    marker = object()

    result = orchestrator.run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        delivery=orchestrator.DeliveryRuleInputs(marker, marker, marker, marker),
    )

    assert calls == ["R-ENT-001", "R-STK-001"]
    assert result.executed_rule_ids == ("R-ENT-001", "R-STK-001")
    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"


def test_orchestrator_partial_execution_reports_coverage(monkeypatch):
    calls: list[str] = []
    _patch_rule(monkeypatch, "evaluate_r_fin_001", "R-FIN-001", "TRUE", calls)
    marker = object()

    result = orchestrator.run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        finance_capacity=orchestrator.FinanceCapacityRuleInputs(
            marker, marker, marker, marker, marker
        ),
    )

    assert calls == ["R-FIN-001"]
    assert result.executed_rule_ids == ("R-FIN-001",)
    assert result.omitted_rule_ids == tuple(
        rule_id for rule_id in ALL_RULES if rule_id != "R-FIN-001"
    )
    assert result.crc_result.consolidated_result == "NO COMPRAR"


def test_orchestrator_without_bundles_preserves_base_result():
    result = orchestrator.run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="NEGOCIAR",
    )

    assert result.executed_rule_ids == ()
    assert result.omitted_rule_ids == ALL_RULES
    assert result.assessments == ()
    assert result.crc_result.consolidated_result == "NEGOCIAR"


def test_orchestrator_delegates_purchase_context_validation_to_public_engine():
    purchase = _purchase().model_copy(update={"scenario_id": "OTHER"})
    with pytest.raises(ValueError, match="scenario_id distintos"):
        orchestrator.run_domain_rules(
            purchase=purchase,
            context=_context(),
            base_result="COMPRAR",
        )
