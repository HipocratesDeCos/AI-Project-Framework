import pytest
from pydantic import ValidationError

from eios.core.negotiation_ladder import (
    LadderContextReferences, LadderRoute, LadderStep, LadderTransition, NegotiationLadderResult,
)


def context(**overrides):
    values = {
        "negotiation_result_id": "NI1", "decision_id": "D1", "scenario_id": "S1",
        "source_references": ("NI_CONTENT_1",),
    }
    values.update(overrides)
    return LadderContextReferences(**values)


def step(step_id="S1", position=1, step_type="OPENING_REQUEST", source="NI_CONTENT_1"):
    return LadderStep(step_id=step_id, step_type=step_type, source_content_reference=source, position=position)


def result(**overrides):
    values = {
        "ladder_id": "L1", "context_references": context(),
        "steps": (step(), step("S2", 2, "CONCESSION", "NI_CONTENT_2")),
        "transitions": (LadderTransition(transition_id="T1", from_step_id="S1", to_step_id="S2", trigger_reference="COND1"),),
        "routes": (LadderRoute(route_id="R1", step_references=("S1", "S2")),),
        "traceability_references": ("TRACE1",),
    }
    values.update(overrides)
    return NegotiationLadderResult(**values)


def test_result_requires_authorized_identity_and_upstream_context():
    value = result()
    assert value.ladder_id == "L1"
    assert value.context_references.negotiation_result_id == "NI1"
    assert value.context_references.decision_id == "D1"
    assert not hasattr(value.context_references, "decision_version")


def test_undefined_decision_version_is_rejected_instead_of_becoming_parallel_identity():
    with pytest.raises(ValidationError):
        LadderContextReferences.model_validate({**context().model_dump(), "decision_version": "DV1"})


def test_each_step_requires_source_content_reference():
    with pytest.raises(ValidationError):
        LadderStep(step_id="S1", step_type="MOVE", position=1, source_content_reference="")


def test_step_ids_are_unique():
    with pytest.raises(ValidationError, match="step_id"):
        result(steps=(step("S1", 1), step("S1", 2, "CONCESSION", "NI2")))


def test_positions_are_unique():
    with pytest.raises(ValidationError, match="position"):
        result(steps=(step("S1", 1), step("S2", 1, "CONCESSION", "NI2")))


def test_transitions_must_reference_existing_steps():
    with pytest.raises(ValidationError, match="step inexistente"):
        result(transitions=(LadderTransition(transition_id="T1", from_step_id="S1", to_step_id="MISSING"),))


def test_routes_must_reference_existing_steps():
    with pytest.raises(ValidationError, match="step inexistente"):
        result(routes=(LadderRoute(route_id="R1", step_references=("S1", "MISSING")),))


def test_traceability_is_required():
    with pytest.raises(ValidationError, match="traceability_references"):
        result(traceability_references=())


def test_result_is_immutable():
    value = result()
    with pytest.raises(ValidationError):
        value.ladder_id = "L2"


def test_structural_fields_are_not_substantive_strategy():
    value = result()
    assert value.steps[0].position == 1
    assert not hasattr(value.steps[0], "strategic_priority")
    assert not hasattr(value.steps[0], "strategy_score")
    assert not hasattr(value, "preferred_route")


@pytest.mark.parametrize("forbidden", [
    "objective_value", "concession_value", "limit_value", "strategic_score",
    "business_decision", "approved", "executed", "scenario_definition", "viability_decision",
])
def test_forbidden_authority_fields_are_rejected(forbidden):
    with pytest.raises(ValidationError):
        NegotiationLadderResult.model_validate({**result().model_dump(), forbidden: "x"})


def test_ladder_references_ni_content_instead_of_redefining_it():
    value = result()
    assert value.steps[0].source_content_reference == "NI_CONTENT_1"
    assert value.steps[1].source_content_reference == "NI_CONTENT_2"
