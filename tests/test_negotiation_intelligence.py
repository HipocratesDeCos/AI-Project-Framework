import pytest
from pydantic import ValidationError

from eios.core.negotiation_intelligence import (
    NIAssertion,
    NIContextReferences,
    NegotiationContent,
    NegotiationIntelligenceResult,
)


def refs(**overrides):
    values = {
        "decision_id": "D1",
        "decision_version": "DV1",
        "scenario_id": "S1",
        "rules_version": "R1",
        "parameters_version": "P1",
        "data_snapshot_id": "SNAP1",
        "viability_reference": "VF1",
        "decision_twin_reference": "DT1",
        "evidence_references": ("E1",),
    }
    values.update(overrides)
    return NIContextReferences(**values)


def result(**overrides):
    values = {
        "negotiation_result_id": "NI1",
        "context_references": refs(),
        "negotiation_content": NegotiationContent(
            objective="reduce total cost",
            opening_request="request improved price",
            moves=("request price reduction",),
            concessions=("offer volume commitment",),
            tradeoffs=("price for volume",),
            fallback="retain current offer",
        ),
        "justification": (
            NIAssertion(
                content="Current price is above the authorized reference.",
                epistemic_type="FACT",
                confidence=1.0,
                source_references=("E1",),
            ),
        ),
        "epistemic_qualifications": (
            NIAssertion(
                content="A lower price may be achievable.",
                epistemic_type="HYPOTHESIS",
                confidence=0.6,
            ),
        ),
        "confidence_uncertainty": (
            NIAssertion(
                content="Outcome depends on supplier response.",
                epistemic_type="ESTIMATE",
                confidence=0.6,
            ),
        ),
        "source_references": ("E1", "VF1", "DT1"),
        "traceability_references": ("TRACE1",),
        "version_identity": "NI1-v1",
    }
    values.update(overrides)
    return NegotiationIntelligenceResult(**values)


def test_result_requires_context_identity_and_version():
    value = result()
    assert value.context_references.decision_id == "D1"
    assert value.context_references.decision_version == "DV1"
    assert value.version_identity == "NI1-v1"


def test_upstream_authorities_are_references_not_redefined_objects():
    value = result()
    assert value.context_references.scenario_id == "S1"
    assert value.context_references.viability_reference == "VF1"
    assert value.context_references.decision_twin_reference == "DT1"


@pytest.mark.parametrize(
    "forbidden",
    ["ladder_step", "sequence_order", "transition", "business_decision", "approved", "executed"],
)
def test_forbidden_authority_fields_are_rejected(forbidden):
    with pytest.raises(ValidationError):
        NegotiationIntelligenceResult.model_validate({**result().model_dump(), forbidden: "x"})


def test_fact_requires_source_reference():
    with pytest.raises(ValidationError, match="source_reference"):
        NIAssertion(content="observed fact", epistemic_type="FACT")


def test_epistemic_types_remain_distinct():
    value = result()
    types = {item.epistemic_type for item in value.justification + value.epistemic_qualifications + value.confidence_uncertainty}
    assert {"FACT", "HYPOTHESIS", "ESTIMATE"} <= types


def test_global_confidence_score_is_not_part_of_contract():
    value = result()
    assert not hasattr(value, "confidence_score")


def test_traceability_is_required():
    with pytest.raises(ValidationError, match="traceability_references"):
        result(traceability_references=())


def test_result_is_immutable():
    value = result()
    with pytest.raises(ValidationError):
        value.negotiation_result_id = "NI2"


def test_new_result_identity_does_not_overwrite_historical_result():
    first = result(negotiation_result_id="NI1", version_identity="NI1-v1")
    second = result(negotiation_result_id="NI2", version_identity="NI2-v1")
    assert first.negotiation_result_id != second.negotiation_result_id
    assert first.version_identity != second.version_identity


def test_negotiation_content_is_not_ladder_structure():
    value = result()
    assert value.negotiation_content.moves == ("request price reduction",)
    assert not hasattr(value.negotiation_content, "sequence_order")
    assert not hasattr(value.negotiation_content, "ladder_step")


def test_hypothesis_does_not_become_scenario_identity():
    value = result()
    hypothesis = value.epistemic_qualifications[0]
    assert hypothesis.epistemic_type == "HYPOTHESIS"
    assert value.context_references.scenario_id == "S1"
