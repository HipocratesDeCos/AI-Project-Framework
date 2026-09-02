import pytest
from pydantic import ValidationError

from eios.core.negotiation_intelligence import (
    NIAssertion, NIContextReferences, NegotiationContent, NegotiationIntelligenceResult,
)


def refs(**overrides):
    values = {
        "decision_id": "D1", "scenario_id": "S1", "rules_version": "R1",
        "parameters_version": "P1", "data_snapshot_id": "SNAP1",
        "viability_reference": "VF1", "decision_twin_reference": "DT1",
        "evidence_references": ("E1",),
    }
    values.update(overrides)
    return NIContextReferences(**values)


def result(**overrides):
    values = {
        "negotiation_result_id": "NI1", "context_references": refs(),
        "negotiation_content": NegotiationContent(
            objective="reduce total cost", opening_request="request improved price",
            moves=("request price reduction",), concessions=("offer volume commitment",),
            tradeoffs=("price for volume",), fallback="retain current offer",
        ),
        "justification": (
            NIAssertion(content="Current price is above the authorized reference.", epistemic_type="FACT", confidence=1.0, source_references=("E1",)),
            NIAssertion(content="A lower price may be achievable.", epistemic_type="HYPOTHESIS", confidence=0.6),
            NIAssertion(content="Outcome depends on supplier response.", epistemic_type="ESTIMATE", confidence=0.6),
        ),
        "traceability_references": ("TRACE1",),
    }
    values.update(overrides)
    return NegotiationIntelligenceResult(**values)


def test_result_requires_authorized_decision_identity_and_result_identity():
    value = result()
    assert value.context_references.decision_id == "D1"
    assert not hasattr(value.context_references, "decision_version")
    assert value.negotiation_result_id == "NI1"


def test_upstream_authorities_are_references_not_redefined_objects():
    value = result()
    assert value.context_references.scenario_id == "S1"
    assert value.context_references.viability_reference == "VF1"
    assert value.context_references.decision_twin_reference == "DT1"


def test_undefined_decision_version_is_rejected_instead_of_becoming_parallel_identity():
    with pytest.raises(ValidationError):
        NIContextReferences.model_validate({**refs().model_dump(), "decision_version": "DV1"})


@pytest.mark.parametrize("forbidden", [
    "ladder_step", "sequence_order", "transition", "business_decision", "approved",
    "executed", "version_identity", "confidence_uncertainty", "epistemic_qualifications",
    "source_references", "confidence_score",
])
def test_forbidden_or_duplicative_fields_are_rejected(forbidden):
    with pytest.raises(ValidationError):
        NegotiationIntelligenceResult.model_validate({**result().model_dump(), forbidden: "x"})


def test_fact_requires_source_reference():
    with pytest.raises(ValidationError, match="source_reference"):
        NIAssertion(content="observed fact", epistemic_type="FACT")


def test_epistemic_types_and_confidence_live_on_single_assertion():
    value = result()
    assert [item.epistemic_type for item in value.justification] == ["FACT", "HYPOTHESIS", "ESTIMATE"]
    assert value.justification[1].confidence == 0.6
    assert value.justification[1].source_references == ()


def test_global_confidence_score_is_not_part_of_contract():
    assert not hasattr(result(), "confidence_score")


def test_traceability_is_required():
    with pytest.raises(ValidationError, match="traceability_references"):
        result(traceability_references=())


def test_result_is_immutable():
    value = result()
    with pytest.raises(ValidationError):
        value.negotiation_result_id = "NI2"


def test_new_result_identity_does_not_overwrite_historical_result():
    first = result(negotiation_result_id="NI1")
    second = result(negotiation_result_id="NI2")
    assert first.negotiation_result_id != second.negotiation_result_id


def test_negotiation_content_is_not_ladder_structure():
    value = result()
    assert value.negotiation_content.moves == ("request price reduction",)
    assert not hasattr(value.negotiation_content, "sequence_order")
    assert not hasattr(value.negotiation_content, "ladder_step")


def test_hypothesis_does_not_become_scenario_identity():
    value = result()
    assert value.justification[1].epistemic_type == "HYPOTHESIS"
    assert value.context_references.scenario_id == "S1"
