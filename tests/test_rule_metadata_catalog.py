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
        "R-DAT-001",
        "R-DAT-002",
        "R-DAT-003",
        "R-ENT-001",
        "R-FIN-001",
        "R-FIN-002",
        "R-FIN-003",
        "R-HIS-001",
        "R-HIS-002",
        "R-HIS-003",
        "R-MGE-001",
        "R-MGE-002",
        "R-MGE-003",
        "R-PAG-001",
        "R-PAG-002",
        "R-PRE-001",
        "R-PRE-002",
        "R-PRE-003",
        "R-PROV-001",
        "R-PROV-002",
        "R-ROT-002",
        "R-STK-001",
        "R-STK-002",
        "R-STK-003",
        "R-STK-004",
    )


@pytest.mark.parametrize(
    ("rule_id", "effect", "severity"),
    (
        ("R-DAT-001", "R3", "INFORMATIVA"),
        ("R-DAT-002", "R3", "MEDIA"),
        ("R-DAT-003", "R0", "CRÍTICA"),
        ("R-ENT-001", "R2", "ALTA"),
        ("R-STK-001", "R1", "ALTA"),
        ("R-STK-002", "R2", "ALTA"),
        ("R-STK-003", "R2", "ALTA"),
        ("R-STK-004", "R1", "ALTA"),
        ("R-FIN-001", "R0", "CRÍTICA"),
        ("R-FIN-002", "R0", "CRÍTICA"),
        ("R-FIN-003", "R1", "ALTA"),
        ("R-HIS-001", "R3", "MEDIA"),
        ("R-HIS-002", "R3", "INFORMATIVA"),
        ("R-HIS-003", "R3", "MEDIA"),
        ("R-MGE-001", "R1", "ALTA"),
        ("R-MGE-002", "R2", "MEDIA"),
        ("R-MGE-003", "R3", "INFORMATIVA"),
        ("R-PAG-001", "R2", "ALTA"),
        ("R-PAG-002", "R1", "ALTA"),
        ("R-PRE-001", "R2", "ALTA"),
        ("R-PRE-002", "R1", "ALTA"),
        ("R-PRE-003", "R3", "INFORMATIVA"),
        ("R-PROV-001", "R2", "MEDIA"),
        ("R-PROV-002", "R2", "ALTA"),
        ("R-ROT-002", "R1", "ALTA"),
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
        authorized_rule_metadata("R-UNKNOWN-001", RULES)
    with pytest.raises(ValueError, match="no materializada"):
        authorized_rule("R-UNKNOWN-001", RULES)


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
            assessments=(_assessment("R-UNKNOWN-001"),),
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


def test_dat003_catalog_carries_authorized_insufficient_result() -> None:
    metadata = authorized_rule_metadata("R-DAT-003", RULES)
    assert metadata.active_result == "INFORMACIÓN INSUFICIENTE"


def test_dat003_true_resolves_to_information_insufficient_not_no_buy() -> None:
    result = run_authorized_assessments_vertical(
        purchase=_purchase(),
        context=_context(),
        assessments=(_assessment("R-DAT-003", "TRUE"),),
        base_result="COMPRAR",
    )
    assert result.crc_result.consolidated_result == "INFORMACIÓN INSUFICIENTE"


def test_dat003_true_precedes_concurrent_no_buy_r0_without_mutation() -> None:
    dat003 = _assessment("R-DAT-003", "TRUE")
    fin = _assessment("R-FIN-001", "TRUE")

    result = run_authorized_assessments_vertical(
        purchase=_purchase(),
        context=_context(),
        assessments=(dat003, fin),
        base_result="COMPRAR",
    )

    assert result.crc_result.consolidated_result == "INFORMACIÓN INSUFICIENTE"
    assert result.crc_result.dominant_reason == dat003.reason
    assert fin.reason in result.crc_result.relevant_factors
    assert "R-FIN-001:R0" in result.crc_result.conflicts
    assert result.assessments[0] == dat003
    assert result.assessments[1] == fin


def test_dat003_false_does_not_precede_concurrent_r0_true() -> None:
    result = run_authorized_assessments_vertical(
        purchase=_purchase(),
        context=_context(),
        assessments=(
            _assessment("R-DAT-003", "FALSE"),
            _assessment("R-FIN-001", "TRUE"),
        ),
        base_result="COMPRAR",
    )
    assert result.crc_result.consolidated_result == "NO COMPRAR"
    assert result.crc_result.dominant_reason == "R-FIN-001 assessment."


def test_dat003_not_evaluable_does_not_absorb_concurrent_r0_true() -> None:
    dat003 = Assessment(
        rule_id="R-DAT-003",
        status="NOT_EVALUABLE",
        outcome=None,
        evidence_ids=["EV-R-DAT-003"],
        reason="R-DAT-003 no evaluable.",
    )
    result = run_authorized_assessments_vertical(
        purchase=_purchase(),
        context=_context(),
        assessments=(
            dat003,
            _assessment("R-FIN-001", "TRUE"),
        ),
        base_result="COMPRAR",
    )
    assert result.crc_result.consolidated_result == "NO COMPRAR"
    assert result.crc_result.dominant_reason == "R-FIN-001 assessment."


def test_pag002_catalog_carries_authorized_conditional_result() -> None:
    metadata = authorized_rule_metadata("R-PAG-002", RULES)
    assert metadata.active_result == "COMPRAR CONDICIONADO"


def test_prov_catalog_carries_authorized_negotiation_results() -> None:
    prov001 = authorized_rule_metadata("R-PROV-001", RULES)
    prov002 = authorized_rule_metadata("R-PROV-002", RULES)
    assert prov001.active_result == "NEGOCIAR"
    assert prov002.active_result == "NEGOCIAR"
