from decimal import Decimal

import pytest

import eios.rules.execution as execution
from eios.core.models import Assessment, DecisionContext, PurchaseOperation


RULES_VERSION = "rules-v1"


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-SVC",
        scenario_id="S-SVC",
        rules_version=RULES_VERSION,
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-SVC",
        scenario_id="S-SVC",
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


def _dummy_bundles():
    marker = object()
    return dict(
        delivery=execution.DeliveryRuleInputs(marker, marker, marker, marker),
        stock_excess=execution.StockExcessRuleInputs(marker, marker),
        stock_absorption=execution.StockAbsorptionRuleInputs(marker, marker),
        finance_capacity=execution.FinanceCapacityRuleInputs(
            marker, marker, marker, marker, marker
        ),
        finance_safety_margin=execution.FinanceSafetyMarginRuleInputs(
            marker, marker, marker, marker, marker, marker, marker
        ),
        history_sufficiency=execution.HistorySufficiencyRuleInputs(
            marker, marker, marker, "COMPANY-1", marker, marker
        ),
    )


def _patch_rule(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    rule_id: str,
    outcome: str,
    calls: list[str],
) -> None:
    def fake(*args, **kwargs):
        assert args[2].rule_id == rule_id
        assert args[2].version == RULES_VERSION
        calls.append(rule_id)
        return _assessment(rule_id, outcome)

    monkeypatch.setattr(execution, name, fake)


def test_service_executes_six_rules_and_consolidates_in_canonical_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    _patch_rule(monkeypatch, "evaluate_r_ent_001", "R-ENT-001", "TRUE", calls)
    _patch_rule(monkeypatch, "evaluate_r_stk_003", "R-STK-003", "TRUE", calls)
    _patch_rule(monkeypatch, "evaluate_r_stk_004", "R-STK-004", "TRUE", calls)
    _patch_rule(monkeypatch, "evaluate_r_fin_001", "R-FIN-001", "FALSE", calls)
    _patch_rule(monkeypatch, "evaluate_r_fin_003", "R-FIN-003", "FALSE", calls)
    _patch_rule(monkeypatch, "evaluate_r_his_002", "R-HIS-002", "TRUE", calls)

    result = execution.run_decision_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        **_dummy_bundles(),
    )

    assert calls == [
        "R-ENT-001",
        "R-STK-003",
        "R-STK-004",
        "R-FIN-001",
        "R-FIN-003",
        "R-HIS-002",
    ]
    assert tuple(item.rule_id for item in result.assessments) == (
        "R-ENT-001",
        "R-FIN-001",
        "R-FIN-003",
        "R-HIS-002",
        "R-STK-003",
        "R-STK-004",
    )
    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"
    assert len(result.traces) == 6
    assert result.c0_capability.result_available is True


def test_service_runs_only_explicitly_supplied_rules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    _patch_rule(monkeypatch, "evaluate_r_fin_001", "R-FIN-001", "TRUE", calls)

    marker = object()
    result = execution.run_decision_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        finance_capacity=execution.FinanceCapacityRuleInputs(
            marker, marker, marker, marker, marker
        ),
    )

    assert calls == ["R-FIN-001"]
    assert tuple(item.rule_id for item in result.assessments) == ("R-FIN-001",)
    assert result.crc_result.consolidated_result == "NO COMPRAR"


def test_service_with_no_rule_inputs_preserves_authorized_base_result() -> None:
    result = execution.run_decision_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="NEGOCIAR",
    )

    assert result.assessments == ()
    assert result.traces == ()
    assert result.crc_result.consolidated_result == "NEGOCIAR"


def test_service_rejects_purchase_context_mismatch_without_rule_inputs() -> None:
    purchase = _purchase().model_copy(update={"scenario_id": "OTHER"})
    with pytest.raises(ValueError, match="scenario_id distintos"):
        execution.run_decision_rules(
            purchase=purchase,
            context=_context(),
            base_result="COMPRAR",
        )
