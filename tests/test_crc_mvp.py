import pytest

from eios.core.crc_mvp import CRCInput, RuleMetadata, resolve_crc
from eios.core.models import Assessment, DecisionContext


def context(version="v1"):
    return DecisionContext(
        decision_id="D1",
        scenario_id="S1",
        rules_version=version,
        parameters_version="p1",
        data_snapshot_id="snap1",
    )


def assessment(rule_id="R1", outcome="TRUE", status="EVALUABLE", reason="ok"):
    return Assessment(
        rule_id=rule_id,
        status=status,
        outcome=outcome,
        evidence_ids=[],
        reason=reason,
    )


def rule(rule_id, effect, severity="MEDIA", version="v1"):
    return RuleMetadata(
        rule_id=rule_id,
        version=version,
        effect=effect,
        severity=severity,
    )


def test_empty_assessments_preserve_baseline():
    result = resolve_crc(
        CRCInput(assessments=[], decision_context=context(), base_result="COMPRAR"),
        {"R1": rule("R1", "R1")},
    )
    assert result.consolidated_result == "COMPRAR"
    assert result.conflicts == ()


def test_r3_is_informative_and_does_not_create_restriction():
    result = resolve_crc(
        CRCInput(assessments=[assessment("R3")], decision_context=context(), base_result="COMPRAR"),
        {"R3": rule("R3", "R3")},
    )
    assert result.consolidated_result == "COMPRAR"
    assert result.dominant_reason == "ok"


def test_r2_produces_negotiation_without_becoming_r0():
    result = resolve_crc(
        CRCInput(assessments=[assessment("R2")], decision_context=context(), base_result="COMPRAR"),
        {"R2": rule("R2", "R2")},
    )
    assert result.consolidated_result == "NEGOCIAR"


def test_r1_produces_conditioned_purchase():
    result = resolve_crc(
        CRCInput(assessments=[assessment("R1")], decision_context=context(), base_result="COMPRAR"),
        {"R1": rule("R1", "R1")},
    )
    assert result.consolidated_result == "COMPRAR CONDICIONADO"


def test_r0_dominates_lower_effects_without_scoring():
    assessments = [
        assessment("R0", reason="critical block"),
        assessment("R1"),
        assessment("R2"),
        assessment("R3"),
    ]
    metadata = {
        "R0": rule("R0", "R0", severity="CRÍTICA"),
        "R1": rule("R1", "R1"),
        "R2": rule("R2", "R2"),
        "R3": rule("R3", "R3"),
    }
    result = resolve_crc(CRCInput(assessments=assessments, decision_context=context(), base_result="COMPRAR"), metadata)
    assert result.consolidated_result == "NO COMPRAR"
    assert result.dominant_reason == "critical block"
    assert result.relevant_factors == ("ok", "ok", "ok")
    assert not hasattr(result, "score")
    assert not hasattr(result, "ranking")


def test_duplicate_r0_does_not_increase_restrictiveness():
    one = resolve_crc(
        CRCInput(assessments=[assessment("R0", reason="same cause")], decision_context=context(), base_result="COMPRAR"),
        {"R0": rule("R0", "R0", severity="CRÍTICA")},
    )
    many = resolve_crc(
        CRCInput(
            assessments=[assessment("R0", reason="same cause"), assessment("R0", reason="same cause")],
            decision_context=context(),
            base_result="COMPRAR",
        ),
        {"R0": rule("R0", "R0", severity="CRÍTICA")},
    )
    assert one.consolidated_result == many.consolidated_result == "NO COMPRAR"


def test_not_evaluable_is_not_false_or_no_purchase():
    result = resolve_crc(
        CRCInput(
            assessments=[assessment("R1", status="NOT_EVALUABLE", outcome=None, reason="missing evidence")],
            decision_context=context(),
            base_result="COMPRAR",
        ),
        {"R1": rule("R1", "R1")},
    )
    assert result.consolidated_result == "INFORMACIÓN INSUFICIENTE"


def test_unknown_rule_is_integrity_error():
    with pytest.raises(ValueError, match="rule_id"):
        resolve_crc(
            CRCInput(assessments=[assessment("UNKNOWN")], decision_context=context(), base_result="COMPRAR"),
            {},
        )


def test_incompatible_rule_version_is_integrity_error():
    with pytest.raises(ValueError, match="rules_version"):
        resolve_crc(
            CRCInput(assessments=[assessment("R1")], decision_context=context("v2"), base_result="COMPRAR"),
            {"R1": rule("R1", "R1", version="v1")},
        )


def test_viable_does_not_force_buy_when_r0_exists():
    result = resolve_crc(
        CRCInput(assessments=[assessment("R0", reason="block")], decision_context=context(), base_result="COMPRAR"),
        {"R0": rule("R0", "R0", severity="CRÍTICA")},
    )
    assert result.consolidated_result == "NO COMPRAR"


def test_historical_scenario_is_not_mixed_with_current_context():
    result = resolve_crc(
        CRCInput(assessments=[assessment("R3", reason="current")], decision_context=context(), base_result="COMPRAR"),
        {"R3": rule("R3", "R3")},
    )
    assert result.traceability.scenario_id == "S1"
    assert result.consolidated_result == "COMPRAR"


@pytest.mark.parametrize("forbidden", ["score", "ranking", "winner", "selected_alternative", "business_decision", "override"])
def test_forbidden_outputs_are_absent(forbidden):
    result = resolve_crc(
        CRCInput(assessments=[assessment("R3")], decision_context=context(), base_result="COMPRAR"),
        {"R3": rule("R3", "R3")},
    )
    assert not hasattr(result, forbidden)
