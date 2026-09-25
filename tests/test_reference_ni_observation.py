"""Same-call synthetic NI capture with C0 trace binding."""
from copy import deepcopy
from hashlib import sha256

import pytest

from examples.reference_business_case_001 import (
    _bundle, _runtime, _provenanced_c0_invoker, _synthetic_negotiation_sources,
    execute_reference_business_case, execute_reference_business_case_with_ni_observation,
)
from eios.core.reference_ni_observation import validate_reference_ni_observation_payload
from eios.core.reference_price_observation import _canonical
from eios.rules.negotiation_provenance import build_reference_observed_c0_bound_ni_invoker
from eios.rules.provenance import AssessmentTraceBinding


@pytest.mark.parametrize("variant", ("negative", "qtg-eligible"))
def test_same_call_ni_and_terminal_unchanged(variant):
    baseline = execute_reference_business_case(variant=variant).to_payload()
    terminal, observation = execute_reference_business_case_with_ni_observation(variant=variant)
    payload = observation.to_payload()
    assert terminal.to_payload() == baseline
    validate_reference_ni_observation_payload(payload, baseline)
    assert payload["authority_origin"] == "DECLARED_SYNTHETIC_TEST_EVIDENCE"
    assert payload["c0_content_derivation_proven"] is False
    assert payload["separate_c0_invocation_binding_proven"] is False
    assert payload["ni_result"]["context_references"]["decision_twin_reference"] is None
    assert payload["ni_execution"] == next(
        item for item in baseline["execution_outcome"]["capability_results"]
        if item["capability"] == "NEGOTIATION_INTELLIGENCE"
    )
    altered = deepcopy(payload)
    altered["ni_result"]["negotiation_content"]["objective"] = "invented"
    with pytest.raises(ValueError, match="fingerprint"):
        validate_reference_ni_observation_payload(altered, baseline)


def test_rehashed_detached_result_rejected():
    terminal, observation = execute_reference_business_case_with_ni_observation(
        variant="negative",
    )
    payload = observation.to_payload()
    payload["ni_result"]["negotiation_content"]["objective"] = "invented"
    payload["ni_result_fingerprint"] = sha256(_canonical(payload["ni_result"])).hexdigest()
    payload["observation_fingerprint"] = sha256(_canonical({
        key: value for key, value in payload.items() if key != "observation_fingerprint"
    })).hexdigest()
    with pytest.raises(ValueError, match="C0-bound replay"):
        validate_reference_ni_observation_payload(payload, terminal.to_payload())


def test_purchase_binding_and_single_use():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    _, assessment, trace = _provenanced_c0_invoker(purchase, context)
    carrier, evidences = _synthetic_negotiation_sources(purchase, context, trace.trace_id)
    kwargs = dict(purchase=purchase, content_evidence=carrier, evidences=evidences,
                  bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
                  reference_case_id="test-case")
    observed = build_reference_observed_c0_bound_ni_invoker(**kwargs)
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()
    with pytest.raises(ValueError, match="currency"):
        observed(purchase.model_copy(update={"currency": "USD"}), context)
    with pytest.raises(ValueError, match="single-use"):
        observed(purchase, context)
    valid = build_reference_observed_c0_bound_ni_invoker(**kwargs)
    capability = valid(purchase, context)
    assert valid.capture().capability == capability
    with pytest.raises(ValueError, match="single-use"):
        valid(purchase, context)


def test_foreign_c0_binding_rejected_before_ni():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    _, assessment, trace = _provenanced_c0_invoker(purchase, context)
    carrier, evidences = _synthetic_negotiation_sources(purchase, context, trace.trace_id)
    bad = assessment.model_copy(update={"reason": "tampered"})
    observed = build_reference_observed_c0_bound_ni_invoker(
        purchase=purchase, content_evidence=carrier, evidences=evidences,
        bindings=(AssessmentTraceBinding(assessment=bad, trace=trace),),
        reference_case_id="test-case",
    )
    with pytest.raises(ValueError):
        observed(purchase, context)
