"""C0/CRC observation preserves the exact provenance-checked O1 invocation."""
from copy import deepcopy

import pytest

from examples.reference_business_case_001 import (
    _bundle, _provenanced_c0_invoker, _runtime,
    execute_reference_business_case,
    execute_reference_business_case_with_c0_observation,
)
from eios.core.reference_c0_observation import validate_reference_c0_observation_payload


@pytest.mark.parametrize("variant,qtg_status", (
    ("negative", "NO_APTO"), ("qtg-eligible", "APTO"),
))
def test_same_run_c0_retains_qtg_divergence_and_terminal(variant, qtg_status):
    original = execute_reference_business_case(variant=variant).to_payload()
    terminal, observation = execute_reference_business_case_with_c0_observation(
        variant=variant,
    )
    payload = observation.to_payload()
    assert terminal.to_payload() == original
    validate_reference_c0_observation_payload(payload, original)
    assert payload["qtg_status"] == qtg_status
    assert payload["qtg_c0_derivation_proven"] is False
    assert payload["crc_base_origin"] == "SUPPLIED_SYNTHETIC_BASE_RESULT"
    assert payload["base_result"] == "COMPRAR"
    assert payload["crc_result"]["consolidated_result"] == "COMPRAR"
    assert payload["vertical_result"]["assessments"][0]["outcome"] == "FALSE"
    assert payload["c0_execution"] == next(
        item for item in original["execution_outcome"]["capability_results"]
        if item["capability"] == "C0"
    )
    changed = deepcopy(payload)
    changed["vertical_result"]["assessments"][0]["outcome"] = "TRUE"
    with pytest.raises(ValueError, match="fingerprint"):
        validate_reference_c0_observation_payload(changed, original)


def test_one_vertical_composition_and_failure_consumes_session(monkeypatch):
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    import eios.rules.provenance as provenance
    original = provenance.run_provenanced_assessments_vertical
    calls = []
    monkeypatch.setattr(provenance, "run_provenanced_assessments_vertical",
                        lambda **kwargs: (calls.append(kwargs), original(**kwargs))[1])
    observed, _, _ = _provenanced_c0_invoker(
        purchase, context, observed=True, reference_case_id="test-case",
    )
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()
    bad = purchase.model_copy(update={"quantity": purchase.quantity + 1})
    with pytest.raises(ValueError, match="input_fingerprint"):
        observed(bad, context)
    assert len(calls) == 1
    with pytest.raises(ValueError, match="single-use"):
        observed(purchase, context)
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()

    valid, _, _ = _provenanced_c0_invoker(
        purchase, context, observed=True, reference_case_id="test-case",
    )
    execution = valid(purchase, context)
    assert len(calls) == 2
    assert valid.capture().capability == execution
    with pytest.raises(ValueError, match="single-use"):
        valid(purchase, context)


def test_context_mismatch_rejects_capture():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    observed, _, _ = _provenanced_c0_invoker(
        purchase, context, observed=True, reference_case_id="test-case",
    )
    with pytest.raises(ValueError, match="Trace.scenario_id"):
        observed(purchase.model_copy(update={"scenario_id": "other"}),
                 context.model_copy(update={"scenario_id": "other"}))
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()
