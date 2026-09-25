"""Same-call Decision Twin observation of the synthetic two-scenario fixture."""
from copy import deepcopy

import pytest

from examples.reference_business_case_001 import (
    _bundle, _runtime, _scenario_sources, _twin_alternatives,
    execute_reference_business_case,
    execute_reference_business_case_with_decision_twin_observation,
)
from eios.core.reference_decision_twin_observation import (
    validate_reference_decision_twin_observation_payload,
)
from eios.rules.decision_twin_integration import build_reference_observed_decision_twin_invoker


@pytest.mark.parametrize("variant", ("negative", "qtg-eligible"))
def test_same_run_comparison_and_terminal_unchanged(variant):
    baseline = execute_reference_business_case(variant=variant).to_payload()
    terminal, observation = execute_reference_business_case_with_decision_twin_observation(
        variant=variant,
    )
    payload = observation.to_payload()
    assert terminal.to_payload() == baseline
    validate_reference_decision_twin_observation_payload(payload, baseline)
    assert payload["alternative_refs"] == ["REF-BUSINESS-001-ALT-1", "REF-BUSINESS-001-ALT-2"]
    assert payload["differences"] == payload["missing_attributes"] == []
    assert payload["selected_alternative"] is None
    assert payload["comparison_scope"] == "STRUCTURAL_DESCRIPTIVE_ONLY"
    assert payload["twin_execution"] == next(
        item for item in baseline["execution_outcome"]["capability_results"]
        if item["capability"] == "DECISION_TWIN"
    )
    changed = deepcopy(payload)
    changed["comparison"]["differences"] = ["viability"]
    with pytest.raises(ValueError, match="fingerprint"):
        validate_reference_decision_twin_observation_payload(changed, baseline)


def test_purchase_mismatch_before_stage2_and_one_shot(monkeypatch):
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    preparation, inputs, _ = _scenario_sources(purchase, context)
    import eios.rules.decision_twin_integration as integration
    original = integration.build_provenanced_decision_twin_comparison
    calls = []
    monkeypatch.setattr(integration, "build_provenanced_decision_twin_comparison",
                        lambda **kwargs: (calls.append(kwargs), original(**kwargs))[1])
    kwargs = dict(
        purchase=purchase, preparation=preparation,
        alternatives=_twin_alternatives(inputs), reference_case_id="test-case",
    )
    observed = build_reference_observed_decision_twin_invoker(**kwargs)
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()
    modified = purchase.model_copy(update={"currency": "USD"})
    with pytest.raises(ValueError, match="currency"):
        observed(modified, context)
    assert calls == []
    with pytest.raises(ValueError, match="single-use"):
        observed(purchase, context)
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()

    valid = build_reference_observed_decision_twin_invoker(**kwargs)
    capability = valid(purchase, context)
    assert len(calls) == 1
    assert valid.capture().capability == capability
    with pytest.raises(ValueError, match="single-use"):
        valid(purchase, context)


def test_foreign_scenario_cannot_be_captured():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    preparation, inputs, _ = _scenario_sources(purchase, context)
    observed = build_reference_observed_decision_twin_invoker(
        purchase=purchase, preparation=preparation,
        alternatives=_twin_alternatives(inputs), reference_case_id="test-case",
    )
    with pytest.raises(ValueError, match="scenario_id"):
        observed(purchase, context.model_copy(update={"scenario_id": "other"}))
    with pytest.raises(ValueError, match="unavailable"):
        observed.capture()
