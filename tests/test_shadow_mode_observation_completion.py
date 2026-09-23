from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from eios.assurance import ObservedHumanDecision, ShadowModeResult, produce_shadow_mode_result
from eios.core.crc_mvp import CRCResult, CRCTraceability
from eios.core.models import DecisionContext, Evidence
from eios.core.mvp_execution import MVP_CAPABILITY_ORDER, run_mvp_execution


RECORDED_AT = datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)
DECIDED_AT = datetime(2026, 9, 23, 12, 5, tzinfo=timezone.utc)


def _context():
    return DecisionContext(
        decision_id="D-SHADOW",
        scenario_id="S-SHADOW",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _crc(result="COMPRAR"):
    return CRCResult(
        consolidated_result=result,
        dominant_reason="shadow test",
        relevant_factors=(),
        conflicts=(),
        traceability=CRCTraceability(
            decision_id="D-SHADOW",
            scenario_id="S-SHADOW",
            rules_version="rules-v1",
            assessment_rule_ids=("R-FIN-001",),
        ),
    )


def _evidences(state="DEMONSTRATED"):
    return (
        Evidence(
            evidence_id="E-AUTH",
            source_type="human-decision",
            source_ref="authority:human",
            captured_at=DECIDED_AT.date(),
            state=state,
            demonstration_ref="authority:human:v1" if state == "DEMONSTRATED" else None,
        ),
        Evidence(
            evidence_id="E-DECISION",
            source_type="human-decision",
            source_ref="decision:human",
            captured_at=DECIDED_AT.date(),
            state=state,
            demonstration_ref="decision:human:1" if state == "DEMONSTRATED" else None,
        ),
    )


def _human(result="COMPRAR", **overrides):
    data = dict(
        decision_id="D-SHADOW",
        scenario_id="S-SHADOW",
        observed_result=result,
        decision_ref="decision:human:1",
        decided_at=DECIDED_AT,
        decision_authority_ref="authority:human:v1",
        evidence_refs=("E-DECISION",),
        trace_refs=("TRACE-HUMAN-1",),
        source_state="OBSERVED",
    )
    data.update(overrides)
    return ObservedHumanDecision(**data)


def _produce(*, crc=None, human=None, visibility="WITHHELD_DECLARED", evidences=None):
    return produce_shadow_mode_result(
        context=_context(),
        crc_result=crc or _crc(),
        execution_ref="execution:o1:shadow-1",
        shadow_evaluation_recorded_at=RECORDED_AT,
        human_decision=human or _human(),
        system_visibility_state=visibility,
        evidences=evidences or _evidences(),
    )


def test_literal_match_is_descriptive_only():
    result = _produce()
    assert result.comparison_state == "MATCH"
    assert result.observation.system_result == "COMPRAR"
    assert result.observation.human_result == "COMPRAR"
    assert any("no juicio de corrección" in item for item in result.limitations)


def test_literal_difference_is_preserved_without_quality_judgment():
    result = _produce(human=_human("NO COMPRAR"))
    assert result.comparison_state == "DIFFERENT"
    assert result.observation.human_result == "NO COMPRAR"


def test_system_information_insufficient_has_explicit_state():
    result = _produce(crc=_crc("INFORMACIÓN INSUFICIENTE"), human=_human("NO COMPRAR"))
    assert result.comparison_state == "SYSTEM_INSUFFICIENT"


def test_human_not_observed_has_explicit_state():
    human = ObservedHumanDecision(
        decision_id="D-SHADOW",
        scenario_id="S-SHADOW",
        source_state="NOT_OBSERVED",
    )
    result = _produce(human=human, evidences=())
    assert result.comparison_state == "HUMAN_NOT_OBSERVED"
    assert result.eligibility == "NOT_SHADOW_ELIGIBLE"
    assert result.observation.human_result is None


def test_human_identity_mismatch_fails_closed():
    with pytest.raises(ValueError, match="decision_id incompatible"):
        _produce(human=_human(decision_id="OTHER"))


def test_crc_context_mismatch_fails_closed():
    bad = _crc().model_copy(
        update={
            "traceability": CRCTraceability(
                decision_id="OTHER",
                scenario_id="S-SHADOW",
                rules_version="rules-v1",
                assessment_rule_ids=("R-FIN-001",),
            )
        }
    )
    with pytest.raises(ValueError, match="CRCResult.decision_id incompatible"):
        _produce(crc=bad)


def test_observed_human_decision_requires_full_provenance():
    with pytest.raises(ValidationError, match="OBSERVED requiere"):
        ObservedHumanDecision(
            decision_id="D-SHADOW",
            scenario_id="S-SHADOW",
            observed_result="COMPRAR",
            source_state="OBSERVED",
        )


def test_gap_does_not_demonstrate_human_decision_authority():
    with pytest.raises(ValueError, match="decision_authority_ref no demostrada"):
        _produce(evidences=_evidences(state="GAP"))


@pytest.mark.parametrize(
    ("visibility", "expected"),
    [
        ("WITHHELD_DECLARED", "SHADOW_ELIGIBLE"),
        ("EXPOSED", "NOT_SHADOW_ELIGIBLE"),
        ("UNKNOWN", "NOT_DETERMINABLE"),
    ],
)
def test_visibility_controls_shadow_eligibility_only(visibility, expected):
    result = _produce(visibility=visibility)
    assert result.eligibility == expected
    assert result.comparison_state == "MATCH"


def test_temporal_inversion_fails_closed():
    early = datetime(2026, 9, 23, 11, 59, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="decided_at no puede ser anterior"):
        _produce(human=_human(decided_at=early))


def test_observation_id_is_deterministic():
    first = _produce()
    second = _produce()
    assert first.observation_id == second.observation_id
    assert first.observation_id.startswith("shadow:D-SHADOW:S-SHADOW:")


def test_result_contract_contains_no_scoring_or_feedback_fields():
    fields = set(ShadowModeResult.model_fields)
    forbidden = {
        "accuracy",
        "score",
        "model_score",
        "winner",
        "correctness",
        "parameter_update",
        "retraining_instruction",
        "recommendation_change",
    }
    assert forbidden.isdisjoint(fields)


def test_shadow_mode_does_not_enter_o1_pipeline():
    assert "SHADOW_MODE" not in MVP_CAPABILITY_ORDER
    assert "shadow_mode_invoker" not in run_mvp_execution.__annotations__


def test_system_provenance_uses_supplied_execution_reference_only():
    result = _produce()
    assert result.observation.system_trace_refs == ("execution:o1:shadow-1",)
    assert "execution:o1:shadow-1" in result.trace_refs
    assert "TRACE-HUMAN-1" in result.trace_refs


def test_synthetic_rehearsal_remains_non_operational():
    result = _produce()
    assert result.eligibility == "SHADOW_ELIGIBLE"
    assert any("declaración de proceso" in item for item in result.limitations)
    assert all(
        term not in ShadowModeResult.model_fields
        for term in ("approved", "executed", "purchase_order", "override")
    )
