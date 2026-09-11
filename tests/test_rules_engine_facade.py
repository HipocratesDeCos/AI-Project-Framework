from decimal import Decimal

import pytest

from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.rules import RulesEngineInput, run_rules_engine


RULES = "rules-v1"


def _context(*, decision_id: str = "D-ENGINE", scenario_id: str = "S-ENGINE") -> DecisionContext:
    return DecisionContext(
        decision_id=decision_id,
        scenario_id=scenario_id,
        rules_version=RULES,
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase(*, decision_id: str = "D-ENGINE", scenario_id: str = "S-ENGINE") -> PurchaseOperation:
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


def _assessment(rule_id: str, outcome: str = "TRUE") -> Assessment:
    return Assessment(
        rule_id=rule_id,
        status="EVALUABLE",
        outcome=outcome,
        evidence_ids=[f"EV-{rule_id}"],
        reason=f"{rule_id} assessment.",
    )


def test_rules_engine_executes_authorized_assessment_set() -> None:
    result = run_rules_engine(
        RulesEngineInput(
            purchase=_purchase(),
            context=_context(),
            assessments=(
                _assessment("R-FIN-001", "FALSE"),
                _assessment("R-STK-003", "TRUE"),
                _assessment("R-HIS-002", "TRUE"),
            ),
            base_result="COMPRAR",
        )
    )

    assert result.crc_result.consolidated_result == "NEGOCIAR"
    assert result.crc_result.dominant_reason == "R-STK-003 assessment."
    assert tuple(item.rule_id for item in result.assessments) == (
        "R-FIN-001",
        "R-STK-003",
        "R-HIS-002",
    )
    assert tuple(trace.rule_id for trace in result.traces) == (
        "R-FIN-001",
        "R-STK-003",
        "R-HIS-002",
    )


def test_rules_engine_preserves_authorized_base_result_when_empty() -> None:
    result = run_rules_engine(
        RulesEngineInput(
            purchase=_purchase(),
            context=_context(),
            assessments=(),
            base_result="COMPRAR CONDICIONADO",
        )
    )

    assert result.assessments == ()
    assert result.traces == ()
    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"


def test_rules_engine_fails_closed_for_uncatalogued_rule() -> None:
    payload = RulesEngineInput(
        purchase=_purchase(),
        context=_context(),
        assessments=(_assessment("R-PRE-001"),),
        base_result="COMPRAR",
    )
    with pytest.raises(ValueError, match="no materializada"):
        run_rules_engine(payload)


def test_rules_engine_rejects_purchase_context_identity_mismatch() -> None:
    with pytest.raises(ValueError, match="decision_id distintos"):
        RulesEngineInput(
            purchase=_purchase(decision_id="D-OTHER"),
            context=_context(),
            assessments=(),
            base_result="COMPRAR",
        )


def test_rules_engine_keeps_not_evaluable_as_not_evaluable() -> None:
    result = run_rules_engine(
        RulesEngineInput(
            purchase=_purchase(),
            context=_context(),
            assessments=(
                Assessment(
                    rule_id="R-FIN-001",
                    status="NOT_EVALUABLE",
                    outcome=None,
                    evidence_ids=["EV-FIN"],
                    reason="R-FIN-001 no evaluable: evidencia insuficiente.",
                ),
            ),
            base_result="COMPRAR",
        )
    )

    assert result.assessments[0].status == "NOT_EVALUABLE"
    assert result.assessments[0].outcome is None
    assert result.crc_result.consolidated_result == "INFORMACIÓN INSUFICIENTE"
