"""Same-call synthetic Ladder capture from C0-bound NI replay."""
from copy import deepcopy
from hashlib import sha256

import pytest

from examples.reference_business_case_001 import (
    _bundle, _runtime, _provenanced_c0_invoker, _synthetic_negotiation_sources,
    execute_reference_business_case, execute_reference_business_case_with_ladder_observation,
)
from eios.core.reference_ladder_observation import validate_reference_ladder_observation_payload
from eios.core.reference_price_observation import _canonical
from eios.rules.negotiation_provenance import build_reference_observed_c0_bound_ladder_invoker
from eios.rules.provenance import AssessmentTraceBinding


@pytest.mark.parametrize("variant", ("negative", "qtg-eligible"))
def test_same_call_structure_and_terminal_unchanged(variant):
    baseline = execute_reference_business_case(variant=variant).to_payload()
    terminal, observation = execute_reference_business_case_with_ladder_observation(variant=variant)
    payload = observation.to_payload()
    assert terminal.to_payload() == baseline
    validate_reference_ladder_observation_payload(payload, baseline)
    assert [step["step_type"] for step in payload["ladder_result"]["steps"]] == [
        "OBJECTIVE", "OPENING_REQUEST", "FALLBACK",
    ]
    assert payload["authority_origin"] == "DECLARED_SYNTHETIC_TEST_EVIDENCE"
    assert payload["separate_ni_invocation_binding_proven"] is False
    assert payload["c0_content_derivation_proven"] is False
    assert payload["ladder_execution"] == next(
        item for item in baseline["execution_outcome"]["capability_results"]
        if item["capability"] == "NEGOTIATION_LADDER"
    )
    altered = deepcopy(payload)
    altered["ladder_result"]["steps"][0]["step_type"] = "MOVE"
    with pytest.raises(ValueError, match="fingerprint"):
        validate_reference_ladder_observation_payload(altered, baseline)


def test_rehashed_detached_structure_rejected():
    terminal, observation = execute_reference_business_case_with_ladder_observation(
        variant="negative",
    )
    payload = observation.to_payload()
    payload["ladder_result"]["steps"][0]["step_type"] = "MOVE"
    payload["ladder_result_fingerprint"] = sha256(_canonical(payload["ladder_result"])).hexdigest()
    payload["observation_fingerprint"] = sha256(_canonical({
        key: value for key, value in payload.items() if key != "observation_fingerprint"
    })).hexdigest()
    with pytest.raises(ValueError, match="C0-bound NI replay"):
        validate_reference_ladder_observation_payload(payload, terminal.to_payload())


def test_foreign_purchase_and_single_use():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    _, assessment, trace = _provenanced_c0_invoker(purchase, context)
    content, evidences = _synthetic_negotiation_sources(purchase, context, trace.trace_id)
    kwargs = dict(purchase=purchase, content_evidence=content, evidences=evidences,
                  bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
                  reference_case_id="test-case")
    observed = build_reference_observed_c0_bound_ladder_invoker(**kwargs)
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()
    with pytest.raises(ValueError, match="currency"):
        observed(purchase.model_copy(update={"currency": "USD"}), context)
    with pytest.raises(ValueError, match="single-use"):
        observed(purchase, context)
    valid = build_reference_observed_c0_bound_ladder_invoker(**kwargs)
    capability = valid(purchase, context)
    assert valid.capture().capability == capability
    with pytest.raises(ValueError, match="single-use"):
        valid(purchase, context)
