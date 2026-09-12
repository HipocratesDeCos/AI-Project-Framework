from decimal import Decimal

import pytest

from eios.core.models import Assessment, DecisionContext, PurchaseOperation, Rule
from eios.rules import authorized_rule, authorized_rule_metadata, implemented_rule_ids
from eios.rules.runtime import (
    bind_authorized_assessment,
    run_assessment_set_vertical,
    run_authorized_assessments_vertical,
)


RULES = "rules-v1"


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-CATALOG",
        scenario_id="S-CATALOG",
        rules_version=RULES,
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-CATALOG",
        scenario_id="S-CATALOG",
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


def test_catalog_contains_exactly_implemented_rules() -> None:
    assert implemented_rule_ids() == (
        "R-ENT-001",
        "R-FIN-001",
        "R-FIN-003",
        "R-HIS-002",
        "R-STK-001",
        "R-STK-003",
        "R-STK-004",
    )


@pytest.mark.parametrize(
    ("rule_id", "effect", "severity"),
    (
        ("R-ENT-001", "R2", "ALTA"),
        ("R-STK-001", "R1", "ALTA"),
        ("R-STK-003", "R2", "ALTA"),
        ("R-STK-004", "R1", "ALTA"),
        ("R-FIN-001", "R0", "CRÍTICA"),
        ("R-FIN-003", "R1", "ALTA"),
        ("R-HIS-002", "R3", "INFORMATIVA"),
    ),
)
def test_catalog_resolves_authorized_metadata(rule_id: str, effect: str, severity: str) -> None:
    metadata = authorized_rule_metadata(rule_id, RULES)
    assert metadata.rule_id == rule_id
    assert metadata.version == RULES
    assert metadata.effect == effect
    assert metadata.severity == severity


def test_catalog_builds_canonical_rule() -> None:
    rule = authorized_rule("R-FIN-001", RULES)
    assert rule == Rule(rule_id="R-FIN-001", version=RULES, requires_evidence=True)


def test_catalog_rejects_unknown_rule() -> None:
    with pytest.raises(ValueError, match="no materializada"):
        authorized_rule_metadata("R-PRE-001", RULES)
    with pytest.raises(ValueError, match="no materializada"):
        authorized_rule("R-PRE-001", RULES)


def test_bind_authorized_assessment_rejects_rule_mismatch() -> None:
    with pytest.raises(ValueError, match="debe coincidir"):
        bind_authorized_assessment(
            Rule(rule_id="R-STK-003", version=RULES, requires_evidence=True),
            _assessment("R-STK-004"),
        )


def test_internal_runtime_uses_catalog_bindings_without_manual_metadata() -> None:
    fin_rule = Rule(rule_id="R-FIN-001", version=RULES, requires_evidence=True)
    stock_rule = Rule(rule_id="R-STK-003", version=RULES, requires_evidence=True)
    history_rule = Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True)

    result = run_assessment_set_vertical(
        purchase=_purchase(),
        context=_context(),
        bindings=(
            bind_authorized_assessment(fin_rule, _assessment("R-FIN-001", "FALSE")),
            bind_authorized_assessment(stock_rule, _assessment("R-STK-003", "TRUE")),
            bind_authorized_assessment(history_rule, _assessment("R-HIS-002", "TRUE")),
        ),
        base_result="COMPRAR",
    )

    assert result.crc_result.consolidated_result == "NEGOCIAR"
    assert result.crc_result.dominant_reason == "R-STK-003 assessment."
    assert tuple(item.rule_id for item in result.assessments) == (
        "R-FIN-001",
        "R-STK-003",
        "R-HIS-002",
    )


def test_same_execution_runtime_requires_assessments_and_context() -> None:
    result = run_authorized_assessments_vertical(
        purchase=_purchase(),
        context=_context(),
        assessments=(
            _assessment("R-FIN-001", "FALSE"),
            _assessment("R-STK-004", "TRUE"),
            _assessment("R-HIS-002", "TRUE"),
        ),
        base_result="COMPRAR",
    )

    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"
    assert result.crc_result.dominant_reason == "R-STK-004 assessment."
    assert tuple(trace.rule_id for trace in result.traces) == (
        "R-FIN-001",
        "R-STK-004",
        "R-HIS-002",
    )
    assert all(trace.rules_version == RULES for trace in result.traces)


def test_same_execution_runtime_fails_closed_for_uncatalogued_rule() -> None:
    with pytest.raises(ValueError, match="no materializada"):
        run_authorized_assessments_vertical(
            purchase=_purchase(),
            context=_context(),
            assessments=(_assessment("R-PRE-001"),),
            base_result="COMPRAR",
        )


def test_same_execution_runtime_rejects_duplicate_rule_ids() -> None:
    with pytest.raises(ValueError, match="duplicados"):
        run_authorized_assessments_vertical(
            purchase=_purchase(),
            context=_context(),
            assessments=(
                _assessment("R-STK-003"),
                _assessment("R-STK-003", "FALSE"),
            ),
            base_result="COMPRAR",
        )
